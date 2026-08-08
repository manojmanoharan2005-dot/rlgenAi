import time
import subprocess
import os
from typing import Dict, Any, List
from core.logging import logger
from utils.file_manager import file_manager
from utils.executable_finder import resolve_executable
from config.settings import settings

class CompilerService:
    def __init__(self):
        pass

    def get_compiler_bin(self) -> str | None:
        return resolve_executable(settings.ICARUS_VERILOG_PATH)

    def check_installed(self) -> bool:
        """Checks if Icarus Verilog is installed and accessible via PATH or settings path."""
        return self.get_compiler_bin() is not None

    def compile_rtl(self, rtl_code: str, testbench_code: str = None) -> Dict[str, Any]:
        """
        Compiles the Verilog RTL code and optional Testbench using Icarus Verilog.
        Returns a dictionary mapping to the CompileResult schema.
        """
        start_time = time.time()
        if testbench_code:
            logger.info("Compilation (RTL+Testbench) Started")
        else:
            logger.info("Compilation Started")
        
        warnings: List[str] = []
        errors: List[str] = []
        binary_name = "design.out"
        
        # 1. Check if compiler is installed
        compiler_bin = self.get_compiler_bin()
        if not compiler_bin:
            error_msg = "Icarus Verilog is not installed or is not available in PATH"
            errors.append(error_msg)
            logger.error(f"Compilation Failed - {error_msg}")
            return {
                "compiled": False,
                "compiler": "Icarus Verilog",
                "binary": None,
                "warnings": warnings,
                "errors": errors,
                "stage": "compilation",
                "error": error_msg
            }
            
        workspace = file_manager.create_temp_workspace()
        
        try:
            # 2. Save RTL to file
            input_file = file_manager.write_file(workspace, "design.v", rtl_code)
            
            # 3. Setup command with argument array (shell=False)
            cmd = [compiler_bin, "-o", binary_name, "design.v"]
            
            if testbench_code:
                tb_file = file_manager.write_file(workspace, "testbench.v", testbench_code)
                cmd.append("testbench.v")
            
            # 4. Execute Compiler safely with timeout
            process = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                shell=False,
                timeout=15 # Security & stability timeout
            )
            
            # 5. Capture stdout, stderr, exit code
            exit_code = process.returncode
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            
            if stdout:
                logger.info(f"Compiler Output:\n{stdout}")
            if stderr:
                logger.info(f"Compiler STDERR:\n{stderr}")
                
            # Parse stderr for warnings and errors
            if stderr:
                for line in stderr.splitlines():
                    if "warning" in line.lower():
                        warnings.append(line)
                    else:
                        errors.append(line)
                        
            is_compiled = exit_code == 0
            
            process_time = time.time() - start_time
            
            if is_compiled:
                logger.info(f"Compilation Finished Successfully - Time: {process_time:.4f}s")
                return {
                    "compiled": True,
                    "compiler": "Icarus Verilog",
                    "binary": binary_name,
                    "warnings": warnings,
                    "errors": errors,
                    "stdout": stdout,
                    "stderr": stderr
                }
            else:
                logger.error(f"Compilation Failed - Exit Code: {exit_code} - Time: {process_time:.4f}s")
                return {
                    "compiled": False,
                    "compiler": "Icarus Verilog",
                    "binary": None,
                    "warnings": warnings,
                    "errors": errors if errors else [stderr or "Compilation failed with non-zero exit code."],
                    "stdout": stdout,
                    "stderr": stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Compilation Failed - Timeout")
            errors.append("Compilation timed out (exceeded 15s timeout limit).")
            return {
                "compiled": False,
                "compiler": "Icarus Verilog",
                "binary": None,
                "warnings": warnings,
                "errors": errors
            }
        except Exception as e:
            logger.error(f"Compilation Failed - Exception: {str(e)}")
            errors.append(f"An unexpected error occurred during compilation: {str(e)}")
            return {
                "compiled": False,
                "compiler": "Icarus Verilog",
                "binary": None,
                "warnings": warnings,
                "errors": errors
            }
        finally:
            # 6. Cleanup workspace safely
            file_manager.cleanup_workspace(workspace)

compiler_service = CompilerService()
