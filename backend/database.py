from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
from config.settings import settings
from core.logging import logger

DATABASE_URL = settings.DATABASE_URL or "postgresql://postgres:postgres@localhost:5432/rtlgen"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None
    SessionLocal = None

Base = declarative_base()

class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    rtl_code = Column(Text, nullable=True)
    testbench_code = Column(Text, nullable=True)
    compilation_status = Column(Boolean, default=False)
    compilation_report = Column(Text, nullable=True)
    simulation_status = Column(Boolean, default=False)
    simulation_report = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("PostgreSQL database tables initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL tables: {e}")

def save_generation_record(
    prompt: str,
    rtl_code: str,
    testbench_code: str | None,
    compilation_status: bool,
    compilation_report: dict,
    simulation_status: bool,
    simulation_report: dict,
    logs: list[str] | str | None
) -> int | None:
    if SessionLocal is None:
        logger.warning("Database session is not available. Record not saved.")
        return None

    db = SessionLocal()
    try:
        record = GenerationHistory(
            prompt=prompt,
            rtl_code=rtl_code,
            testbench_code=testbench_code,
            compilation_status=compilation_status,
            compilation_report=json.dumps(compilation_report),
            simulation_status=simulation_status,
            simulation_report=json.dumps(simulation_report),
            logs=json.dumps(logs) if isinstance(logs, list) else (logs or ""),
            created_at=datetime.utcnow()
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"Saved generation record #{record.id} to PostgreSQL.")
        return record.id
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save generation record to PostgreSQL: {e}")
        return None
    finally:
        db.close()
