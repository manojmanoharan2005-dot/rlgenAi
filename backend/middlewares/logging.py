import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.logging import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        logger.info(f"Incoming Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url} - Time: {process_time:.4f}s")
            raise e
            
        process_time = time.time() - start_time
        logger.info(f"Completed Request: {request.method} {request.url} - Status: {response.status_code} - Response Time: {process_time:.4f}s")
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
