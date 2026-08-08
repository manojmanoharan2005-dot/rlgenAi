export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export interface CompileResult {
  compiled: boolean;
  compiler: string;
  binary: string | null;
  warnings: string[];
  errors: string[];
}

export interface SimulationResult {
  passed: boolean;
  execution_time: string | null;
  logs: string[] | null;
  errors: string[] | null;
}

export interface GenerateResponse {
  success: boolean;
  provider: string;
  model: string;
  rtl: string;
  testbench: string | null;
  validation: ValidationResult;
  compilation: CompileResult;
  simulation: SimulationResult;
}
