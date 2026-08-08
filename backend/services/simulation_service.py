import time
import subprocess
from typing import Dict, Any, List
from core.logging import logger
from utils.file_manager import file_manager
from utils.executable_finder import resolve_executable
from config.settings import settings

class SimulationService:
    def __init__(self):
        pass

    def get_vvp_bin(self) -> str | None:
        return resolve_executable(settings.VVP_PATH)

    def get_compiler_bin(self) -> str | None:
        return resolve_executable(settings.ICARUS_VERILOG_PATH)

    def check_installed(self) -> bool:
        """Checks if Icarus Simulator (vvp) is installed in the system PATH or configured path."""
        return self.get_vvp_bin() is not None

    def simulate_rtl(self, rtl_code: str, testbench_code: str = None) -> Dict[str, Any]:
        """
        Compiles and simulates Verilog RTL code and optional Testbench using iverilog + vvp.
        Returns a dictionary mapping to the SimulationResult schema.
        """
        start_time = time.time()
        logger.info("Simulation Started")
        
        vvp_bin = self.get_vvp_bin()
        compiler_bin = self.get_compiler_bin()
        
        # 1. Check if simulator is installed
        if not vvp_bin:
            logger.error("Simulation Failed - vvp (Icarus Verilog) not installed or not available in PATH")
            return {
                "passed": False,
                "execution_time": None,
                "logs": [],
                "errors": ["vvp (Icarus Verilog) is not installed or is not available in PATH."]
            }
            
        if not compiler_bin:
            logger.error("Simulation Failed - iverilog compiler not installed or not available in PATH")
            return {
                "passed": False,
                "execution_time": None,
                "logs": [],
                "errors": ["iverilog is not installed or is not available in PATH."]
            }
            
        workspace = file_manager.create_temp_workspace()
        
        try:
            # 2. Save RTL to file and compile it
            file_manager.write_file(workspace, "design.v", rtl_code)
            
            cmd = [compiler_bin, "-o", "simulation.out", "design.v"]
            if testbench_code:
                 file_manager.write_file(workspace, "testbench.v", testbench_code)
                 cmd.append("testbench.v")
            
            comp_process = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                shell=False,
                timeout=15
            )
            
            if comp_process.returncode != 0:
                 return {
                     "passed": False,
                     "execution_time": None,
                     "logs": [],
                     "errors": ["Simulation compilation failed: " + comp_process.stderr.strip()]
                 }
                 
            # 3. Run the compiled simulation binary via vvp
            sim_process = subprocess.run(
                [vvp_bin, "simulation.out"],
                cwd=workspace,
                capture_output=True,
                text=True,
                shell=False,
                timeout=15
            )
            
            exit_code = sim_process.returncode
            stdout = sim_process.stdout.strip()
            stderr = sim_process.stderr.strip()
            
            logs: List[str] = []
            errors: List[str] = []
            
            if stdout:
                logs.extend(stdout.splitlines())
            if stderr:
                errors.extend(stderr.splitlines())
                
            # Check if simulation produced failure indicator in stdout
            stdout_lower = stdout.lower()
            sim_failed_keyword = "fail" in stdout_lower or "error" in stdout_lower or exit_code != 0
            
            is_passed = exit_code == 0 and not ("fail" in stdout_lower and "pass" not in stdout_lower)
            
            process_time = time.time() - start_time
            formatted_time = f"{process_time:.2f}s"
            
            if is_passed:
                logger.info(f"Simulation Finished Successfully - Time: {formatted_time}")
                return {
                    "passed": True,
                    "execution_time": formatted_time,
                    "logs": logs if logs else ["Simulation completed successfully with output."],
                    "errors": errors if errors else []
                }
            else:
                logger.error(f"Simulation Failed - Exit Code: {exit_code} - Time: {formatted_time}")
                return {
                    "passed": False,
                    "execution_time": formatted_time,
                    "logs": logs if logs else [],
                    "errors": errors if errors else ["Simulation check failed or non-zero exit code."]
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Simulation Failed - Timeout")
            return {
                "passed": False,
                "execution_time": None,
                "logs": [],
                "errors": ["Simulation timed out (exceeded 15s limit)."]
            }
        except Exception as e:
            logger.error(f"Simulation Failed - Exception: {str(e)}")
            return {
                "passed": False,
                "execution_time": None,
                "logs": [],
                "errors": [f"An unexpected error occurred during simulation: {str(e)}"]
            }
        finally:
            # 5. Cleanup
            file_manager.cleanup_workspace(workspace)

simulation_service = SimulationService()
