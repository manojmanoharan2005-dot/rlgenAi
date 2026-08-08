from pydantic import BaseModel, Field

class SimulationRequest(BaseModel):
    rtl: str = Field(..., description="Verilog RTL string to simulate")
