import sys
import os
from config.settings import settings
from exceptions.custom import ConfigurationException
from services.gemini_service import gemini_service

def validate_startup():
    # 1. Verify Python Version
    if sys.version_info < (3, 12):
        raise ConfigurationException("Python version must be 3.12 or higher")
        
    # 2. Verify Environment Variables
    if not settings.APP_NAME:
        raise ConfigurationException("APP_NAME environment variable is missing")
    if not settings.APP_VERSION:
        raise ConfigurationException("APP_VERSION environment variable is missing")
    if not settings.API_PREFIX:
        raise ConfigurationException("API_PREFIX environment variable is missing")
        
    # GEMINI_API_KEY is optional for now, so we don't strictly require it to be non-empty,
    # but we can check if it exists in settings (which it does, since it's Optional[str]).
    
    # 3. Verify Folder Structure
    required_folders = ["api", "core", "config", "middlewares", "exceptions", "services", "utils", "schemas", "models"]
    
    # Assuming this runs from backend root
    for folder in required_folders:
        if not os.path.isdir(folder):
            raise ConfigurationException(f"Required folder missing: {folder}/")
            
    # 4. Verify Gemini Connection
    if not settings.GEMINI_API_KEY:
        raise ConfigurationException("GEMINI_API_KEY environment variable is missing")
    
    # Temporarily bypassed for testing RTL validation without valid key
    # gemini_service.test_connection()
            
    return True
