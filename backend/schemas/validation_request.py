from pydantic import BaseModel, Field

class ValidationRequest(BaseModel):
    rtl: str = Field(..., description="Verilog RTL string to validate")
