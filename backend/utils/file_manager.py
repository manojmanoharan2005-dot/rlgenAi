import os
import shutil
import tempfile
from typing import Tuple
from core.logging import logger

class FileManager:
    @staticmethod
    def create_temp_workspace() -> str:
        """Creates a temporary working directory and returns its path."""
        workspace = tempfile.mkdtemp(prefix="rtlgen_")
        logger.info(f"Created temporary workspace at {workspace}")
        return workspace

    @staticmethod
    def write_file(workspace: str, filename: str, content: str) -> str:
        """Writes content to a file in the workspace and returns its full path."""
        file_path = os.path.join(workspace, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    @staticmethod
    def cleanup_workspace(workspace: str):
        """Deletes the temporary working directory and all its contents."""
        try:
            if os.path.exists(workspace):
                shutil.rmtree(workspace)
                logger.info(f"Cleaned up workspace at {workspace}")
        except Exception as e:
            logger.warning(f"Failed to clean up workspace {workspace}: {str(e)}")

file_manager = FileManager()
