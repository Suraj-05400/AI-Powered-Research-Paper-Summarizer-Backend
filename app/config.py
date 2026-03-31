'''
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Fix: Use os.getenv to provide a fallback so it's never "None"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research_analyzer.db")
    
    # Fix: Provide a default string so Pydantic doesn't complain if Env Var is missing
    SECRET_KEY: str = os.getenv("SECRET_KEY", "temporary_dev_key_12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Use Optional for things that can actually be None
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    
    # Add defaults for everything else
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        extra = "ignore" # This tells Pydantic to ignore extra env vars it doesn't recognize

'''
'''
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database: Use Environment variable for Render (Postgres), fallback to SQLite for local
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research_analyzer.db")
    
    # JWT: CRITICAL FIX
    # We use a static fallback for local, but MUST use an Env Var in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "7e8f92b1c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week (Better for UX)
    
    # API Keys (Loaded from Render Environment Variables)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Google Configuration
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Environment Detection
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://researchpaperpro.netlify.app")
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    UPLOAD_DIRECTORY: str = "./uploadedpapers"
    
    # Redis (Render often uses an Internal Redis URL)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
'''
'''
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import model_validator
import os

class Settings(BaseSettings):
    # Database
    #DATABASE_URL: str = "sqlite:///./research_analyzer.db"
    raw_database_url: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./research_analyzer.db"
    )

# CRITICAL FIX: This automatically converts postgres:// to postgresql://
    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def fix_postgres_protocol(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    #SECRET_KEY: str = secrets.token_hex(32) #"your-secret-key-change-in-production"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research_analyzer.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-change-in-render-env-vars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Google Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_TRANSLATE_CREDENTIALS_PATH: Optional[str] = None
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    UPLOAD_DIRECTORY: str = "./uploadedpapers"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file =".env"
        case_sensitive = True

settings = Settings()
'''

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator # Use model_validator instead
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research_analyzer.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-dev-key-12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    UPLOAD_DIRECTORY: str = "./uploadedpapers"
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # This validator runs on the whole model after fields are set
    @model_validator(mode="after")
    def fix_postgres_protocol(self) -> "Settings":
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True, 
        extra="ignore" 
    )

settings = Settings()
