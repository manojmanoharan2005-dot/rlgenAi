import sys
import os
# pyrefly: ignore [missing-import]
from config.settings import settings
# pyrefly: ignore [missing-import]
from exceptions.custom import ConfigurationException
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
        
    # 3. Ensure Folder Structure Exists
    required_folders = ["api", "core", "config", "middlewares", "exceptions", "services", "utils", "schemas", "models", "logs"]
    for folder in required_folders:
        os.makedirs(folder, exist_ok=True)
            
    # 4. Check Gemini Key
    if not settings.GEMINI_API_KEY:
        from core.logging import logger
        logger.warning("GEMINI_API_KEY environment variable is missing. Gemini generation features will require API key setup.")

    
    # Temporarily bypassed for testing RTL validation without valid key
    # gemini_service.test_connection()
            
    return True
