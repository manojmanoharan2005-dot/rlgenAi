import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

load_dotenv(override=True)

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    API_PREFIX: str
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.5-flash"
    ICARUS_VERILOG_PATH: str = "iverilog"
    VVP_PATH: str = "vvp"
    DATABASE_URL: Optional[str] = "postgresql+psycopg://postgres:postgres@localhost:5432/rtlgen"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

