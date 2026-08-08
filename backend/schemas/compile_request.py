from pydantic import BaseModel, Field

class CompileRequest(BaseModel):
    rtl: str = Field(..., description="Verilog RTL string to compile")
