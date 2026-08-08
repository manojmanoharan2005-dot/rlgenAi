from pydantic import BaseModel
from typing import Optional
from schemas.validation_response import ValidationResult
from schemas.compile_response import CompileResult
from schemas.simulation_response import SimulationResult

class GenerateResponse(BaseModel):
    success: bool
    provider: str
    model: str
    rtl: str
    testbench: Optional[str] = None
    validation: ValidationResult
    compilation: CompileResult
    simulation: SimulationResult
