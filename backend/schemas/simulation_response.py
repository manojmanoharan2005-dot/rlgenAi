from pydantic import BaseModel
from typing import List, Optional

class SimulationResult(BaseModel):
    passed: bool
    execution_time: Optional[str] = None
    logs: Optional[List[str]] = None
    errors: Optional[List[str]] = None

class SimulationResponse(BaseModel):
    success: bool
    simulation: SimulationResult
