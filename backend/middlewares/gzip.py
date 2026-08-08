from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

def setup_gzip(app: FastAPI):
    app.add_middleware(GZipMiddleware, minimum_size=1000)
