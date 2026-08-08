from pydantic import BaseModel
from typing import List, Optional

class CompileResult(BaseModel):
    compiled: bool
    compiler: str
    binary: Optional[str] = None
    warnings: List[str]
    errors: List[str]

class CompileResponse(BaseModel):
    success: bool
    compilation: CompileResult
