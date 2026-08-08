import time
from typing import Dict, Any
from core.logging import logger
from services.gemini_service import gemini_service
from services.compiler_service import compiler_service
from services.simulation_service import simulation_service
from services.prompts import get_testbench_prompt

class TestbenchService:
    def __init__(self):
        pass

    def generate_and_test(self, rtl_code: str) -> Dict[str, Any]:
        """
        Generates a testbench, compiles both RTL and TB, and simulates them.
        Returns a dictionary representing the testbench step execution.
        """
        start_time = time.time()
        logger.info("Testbench Generation Started")
        
        # 1. Generate Testbench via Gemini
        prompt = get_testbench_prompt(rtl_code)
        try:
            tb_code = gemini_service.generate_rtl(prompt)
            logger.info("Testbench Generated")
        except Exception as e:
            logger.error(f"Testbench Generation Failed: {str(e)}")
            return {
                "success": False,
                "testbench": "",
                "compiled": False,
                "simulation_passed": False,
                "compile_result": {
                    "compiled": False,
                    "compiler": "Icarus Verilog",
                    "binary": None,
                    "warnings": [],
                    "errors": [f"Testbench generation failed: {str(e)}"]
                },
                "sim_result": {
                    "passed": False,
                    "execution_time": None,
                    "logs": [],
                    "errors": ["Testbench generation failed."]
                },
                "logs": [f"Testbench generation failed: {str(e)}"]
            }
            
        # 2. Compile RTL + TB
        compile_result = compiler_service.compile_rtl(rtl_code, tb_code)
        is_compiled = compile_result.get("compiled", False)
        
        if not is_compiled:
            return {
                "success": False,
                "testbench": tb_code,
                "compiled": False,
                "simulation_passed": False,
                "compile_result": compile_result,
                "sim_result": {
                    "passed": False,
                    "execution_time": None,
                    "logs": [],
                    "errors": ["Simulation skipped due to compilation failure."]
                },
                "logs": compile_result.get("errors", []) + compile_result.get("warnings", [])
            }
            
        # 3. Simulate RTL + TB
        sim_result = simulation_service.simulate_rtl(rtl_code, tb_code)
        is_sim_passed = sim_result.get("passed", False)
        
        return {
            "success": is_sim_passed,
            "testbench": tb_code,
            "compiled": True,
            "simulation_passed": is_sim_passed,
            "compile_result": compile_result,
            "sim_result": sim_result,
            "logs": sim_result.get("logs", []) if is_sim_passed else (sim_result.get("errors", []) or sim_result.get("logs", []))
        }

testbench_service = TestbenchService()
