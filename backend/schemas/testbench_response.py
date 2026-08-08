from pydantic import BaseModel
from typing import List, Optional

class TestbenchResponse(BaseModel):
    success: bool
    testbench: str
    compiled: bool
    simulation_passed: bool
    logs: Optional[List[str]] = None
