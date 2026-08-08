from pydantic import BaseModel, Field

class TestbenchRequest(BaseModel):
    rtl: str = Field(..., description="Verilog RTL string to generate a testbench for")
