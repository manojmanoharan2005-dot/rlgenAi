from pydantic import BaseModel
from typing import List

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str]

class ValidationResponse(BaseModel):
    success: bool
    validation: ValidationResult
