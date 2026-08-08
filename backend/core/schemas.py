from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    specification: str = Field(..., description="Natural language specification of the hardware module")

class VerificationLogs(BaseModel):
    success: bool
    logs: str

class GenerateResponseData(BaseModel):
    rtl_code: str
    testbench: str
    compilation: VerificationLogs
    simulation: VerificationLogs

class GenerateResponse(BaseModel):
    status: str
    data: Optional[GenerateResponseData] = None
    error: Optional[str] = None
