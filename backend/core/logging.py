import logging
import sys
import os

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("rtlgen")
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times if module is reloaded
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler
        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

logger = setup_logging()
