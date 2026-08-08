import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

load_dotenv(override=True)

class Settings(BaseSettings):
    APP_NAME: str = "RTLGen AI"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.5-flash"
    ICARUS_VERILOG_PATH: str = "iverilog"
    VVP_PATH: str = "vvp"
    DATABASE_URL: Optional[str] = "postgresql://postgres:postgres@localhost:5432/rtlgen"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

