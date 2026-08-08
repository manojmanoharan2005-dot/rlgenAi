from fastapi import Request
from fastapi.responses import JSONResponse
from core.logging import logger
from exceptions.custom import BaseAppException

async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, BaseAppException):
        logger.error(f"Handled Exception: {exc.__class__.__name__} - {exc.message}")
        error_name = exc.__class__.__name__.replace('Exception', ' Error').strip()
        if error_name == "BaseApp Error":
             error_name = "Application Error"
             
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": error_name,
                "message": exc.message,
                "code": exc.code
            }
        )
        
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "code": "INTERNAL_SERVER_ERROR"
        },
    )
