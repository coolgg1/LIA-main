from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from daemon.config import get_settings
from daemon.models.base import Base
import os

# Get settings
settings = get_settings()

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database schema."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Dependency for FastAPI to inject DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()