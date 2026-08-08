import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from backend.config.settings import settings
except ImportError:
    from config.settings import settings

try:
    from backend.exceptions.custom import ConfigurationException
except ImportError:
    from exceptions.custom import ConfigurationException

try:
    from backend.services.gemini_service import gemini_service
except ImportError:
    from services.gemini_service import gemini_service


def validate_startup():
    # 1. Verify Python Version
    if sys.version_info < (3, 10):
        raise ConfigurationException("Python version must be 3.10 or higher")
        
    # 2. Verify Environment Variables
    if not settings.APP_NAME:
        raise ConfigurationException("APP_NAME environment variable is missing")
    if not settings.APP_VERSION:
        raise ConfigurationException("APP_VERSION environment variable is missing")
    if not settings.API_PREFIX:
        raise ConfigurationException("API_PREFIX environment variable is missing")
        
    # 3. Verify Folder Structure
    required_folders = ["api", "core", "config", "middlewares", "exceptions", "services", "utils", "schemas", "models"]
    
    # Assuming this runs from backend root
    for folder in required_folders:
        if not os.path.isdir(folder):
            raise ConfigurationException(f"Required folder missing: {folder}/")
            
    # 4. Check Gemini Key
    if not settings.GEMINI_API_KEY:
        from core.logging import logger
        logger.warning("GEMINI_API_KEY environment variable is missing. Gemini generation features will require API key setup.")

    
    # Temporarily bypassed for testing RTL validation without valid key
    # gemini_service.test_connection()
            
    return True
