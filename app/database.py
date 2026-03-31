from sqlalchemy import create_engine, String, Integer, Column, DateTime, Text, ForeignKey,JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from app.config import settings
import os

# Load environment variables
load_dotenv()

DATABASE_URL = settings.DATABASE_URL
# Fix Render's postgres:// prefix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# Create database engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from app import models
    Base.metadata.create_all(bind=engine)
