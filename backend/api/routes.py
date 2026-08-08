from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from config.settings import settings
from services.gemini_service import gemini_service
from services.rtl_validator import rtl_validator
from services.compiler_service import compiler_service
from services.simulation_service import simulation_service
from services.testbench_service import testbench_service
from services.prompts import get_rtl_prompt
from schemas.generate_request import GenerateRequest
from schemas.generate_response import GenerateResponse
from schemas.validation_request import ValidationRequest
from schemas.validation_response import ValidationResponse, ValidationResult
from schemas.compile_request import CompileRequest
from schemas.compile_response import CompileResponse, CompileResult
from schemas.simulation_request import SimulationRequest
from schemas.simulation_response import SimulationResponse, SimulationResult
from schemas.testbench_request import TestbenchRequest
from schemas.testbench_response import TestbenchResponse
from database import save_generation_record, SessionLocal, GenerationHistory

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/details")
async def health_details():
    iverilog_installed = compiler_service.check_installed()
    vvp_installed = simulation_service.check_installed()
    return {
        "server": "healthy",
        "gemini": "connected" if settings.GEMINI_API_KEY else "not_configured",
        "model": settings.GEMINI_MODEL,
        "python": "3.12",
        "pyverilog": "installed",
        "validator": "ready",
        "iverilog": "installed" if iverilog_installed else "missing",
        "compiler": "ready" if iverilog_installed else "unavailable",
        "vvp": "installed" if vvp_installed else "missing",
        "simulation": "ready" if vvp_installed else "unavailable",
        "testbench": "ready"
    }

@router.get("/version")
async def app_version():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.post(f"{settings.API_PREFIX}/validate", response_model=ValidationResponse)
async def validate_rtl(request: ValidationRequest):
    is_valid, errors = rtl_validator.validate(request.rtl)
    return ValidationResponse(
        success=True,
        validation=ValidationResult(valid=is_valid, errors=errors)
    )

@router.post(f"{settings.API_PREFIX}/compile", response_model=CompileResponse)
async def compile_rtl(request: CompileRequest):
    if not compiler_service.check_installed():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "stage": "compilation",
                "error": "Icarus Verilog is not installed or is not available in PATH"
            }
        )
    compile_dict = compiler_service.compile_rtl(request.rtl)
    return CompileResponse(
        success=compile_dict.get("compiled", False),
        compilation=CompileResult(
            compiled=compile_dict.get("compiled", False),
            compiler=compile_dict.get("compiler", "Icarus Verilog"),
            binary=compile_dict.get("binary"),
            warnings=compile_dict.get("warnings", []),
            errors=compile_dict.get("errors", [])
        )
    )

@router.post(f"{settings.API_PREFIX}/simulate", response_model=SimulationResponse)
async def simulate_rtl(request: SimulationRequest):
    if not simulation_service.check_installed():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "stage": "simulation",
                "error": "Icarus Verilog simulator (vvp) is not installed or is not available in PATH"
            }
        )
    sim_dict = simulation_service.simulate_rtl(request.rtl)
    return SimulationResponse(
        success=sim_dict.get("passed", False),
        simulation=SimulationResult(
            passed=sim_dict.get("passed", False),
            execution_time=sim_dict.get("execution_time"),
            logs=sim_dict.get("logs"),
            errors=sim_dict.get("errors")
        )
    )

@router.post(f"{settings.API_PREFIX}/testbench", response_model=TestbenchResponse)
async def generate_testbench(request: TestbenchRequest):
    tb_dict = testbench_service.generate_and_test(request.rtl)
    return TestbenchResponse(
        success=tb_dict.get("success", False),
        testbench=tb_dict.get("testbench", ""),
        compiled=tb_dict.get("compiled", False),
        simulation_passed=tb_dict.get("simulation_passed", False),
        logs=tb_dict.get("logs", [])
    )

@router.post(f"{settings.API_PREFIX}/generate", response_model=GenerateResponse)
async def generate_rtl(request: GenerateRequest):
    prompt = get_rtl_prompt(request.prompt)
    rtl_code = gemini_service.generate_rtl(prompt)
    
    is_valid, errors = rtl_validator.validate(rtl_code)
    
    tb_code = None
    compile_dict = {}
    sim_dict = {}

    if is_valid:
        # Pipeline: Generate RTL -> Generate TB -> Compile (RTL+TB) -> Simulate (vvp)
        tb_dict = testbench_service.generate_and_test(rtl_code)
        tb_code = tb_dict.get("testbench", "")
        
        compile_res = tb_dict.get("compile_result", {})
        sim_res = tb_dict.get("sim_result", {})
        
        compile_dict = {
            "compiled": compile_res.get("compiled", False),
            "compiler": compile_res.get("compiler", "Icarus Verilog"),
            "binary": compile_res.get("binary"),
            "warnings": compile_res.get("warnings", []),
            "errors": compile_res.get("errors", [])
        }
        
        sim_dict = {
            "passed": sim_res.get("passed", False),
            "execution_time": sim_res.get("execution_time"),
            "logs": sim_res.get("logs"),
            "errors": sim_res.get("errors")
        }
    else:
        compile_dict = {
            "compiled": False,
            "compiler": "Icarus Verilog",
            "binary": None,
            "warnings": [],
            "errors": ["Compilation skipped due to validation failures."]
        }
        sim_dict = {
            "passed": False,
            "execution_time": None,
            "logs": None,
            "errors": ["Simulation skipped due to validation failures."]
        }
    
    overall_success = is_valid and compile_dict.get("compiled", False) and sim_dict.get("passed", False)

    # Step 9: Save generation history into PostgreSQL database
    all_logs = (sim_dict.get("logs") or []) + (compile_dict.get("errors") or []) + (sim_dict.get("errors") or [])
    save_generation_record(
        prompt=request.prompt,
        rtl_code=rtl_code,
        testbench_code=tb_code,
        compilation_status=compile_dict.get("compiled", False),
        compilation_report=compile_dict,
        simulation_status=sim_dict.get("passed", False),
        simulation_report=sim_dict,
        logs=all_logs
    )

    return GenerateResponse(
        success=overall_success,
        provider="gemini",
        model=settings.GEMINI_MODEL,
        rtl=rtl_code,
        testbench=tb_code,
        validation=ValidationResult(valid=is_valid, errors=errors),
        compilation=CompileResult(**compile_dict),
        simulation=SimulationResult(**sim_dict)
    )

@router.get(f"{settings.API_PREFIX}/history")
async def get_history():
    """Fetch generation history from PostgreSQL database."""
    if SessionLocal is None:
        return []
    db = SessionLocal()
    try:
        records = db.query(GenerationHistory).order_by(GenerationHistory.created_at.desc()).limit(20).all()
        return [
            {
                "id": r.id,
                "prompt": r.prompt,
                "compilation_status": r.compilation_status,
                "simulation_status": r.simulation_status,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
