import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from api.routes import router as api_router
from config.settings import settings
from core.exceptions import global_exception_handler
from core.logging import logger
from core.validation import validate_startup
from middlewares.logging import RequestLoggingMiddleware
from middlewares.cors import setup_cors
from middlewares.gzip import setup_gzip
from exceptions.custom import BaseAppException

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",  # Explicitly enable swagger
    redoc_url="/redoc"
)

# Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(BaseAppException, global_exception_handler)

# Middlewares (Order matters: outermost first)
app.add_middleware(RequestLoggingMiddleware)
setup_gzip(app)
setup_cors(app)

# Include Routes
app.include_router(api_router)

@app.on_event("startup")
async def on_startup():
    try:
        validate_startup()
        from database import init_db
        init_db()
        logger.info("Application Started")
    except Exception as e:
        logger.error(f"Startup Validation Failed: {str(e)}")
        sys.exit(1)

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application Shutdown")
