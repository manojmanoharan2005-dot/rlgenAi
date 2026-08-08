import os
import shutil
from typing import Optional
from core.logging import logger

def resolve_executable(cmd_setting: str) -> Optional[str]:
    """
    Resolves an executable path from settings/environment variable or system PATH.
    Supports:
    1. Direct binary name in PATH (e.g. 'iverilog')
    2. Absolute path (e.g. 'C:\\iverilog\\bin\\iverilog.exe')
    3. Relative path or path with extension
    """
    if not cmd_setting:
        return None

    # Check if direct absolute file path exists
    if os.path.isabs(cmd_setting) or os.sep in cmd_setting or "/" in cmd_setting:
        if os.path.exists(cmd_setting) and os.path.isfile(cmd_setting):
            return cmd_setting
        # Check with .exe on Windows
        if os.name == 'nt' and not cmd_setting.lower().endswith('.exe'):
            exe_path = cmd_setting + '.exe'
            if os.path.exists(exe_path) and os.path.isfile(exe_path):
                return exe_path
        logger.warning(f"Specified executable path '{cmd_setting}' does not exist on disk.")

    # Fallback / primary search via PATH
    found = shutil.which(cmd_setting)
    if found:
        return found
        
    return None
