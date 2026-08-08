from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

def setup_cors(app: FastAPI):
    origins_str = settings.CORS_ORIGINS or "*"
    if origins_str.strip() == "*":
        origins = ["*"]
        allow_credentials = False
    else:
        origins = [o.strip() for o in origins_str.split(",") if o.strip()]
        allow_credentials = True

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
