from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./codecrafts.db")
    
    # JWT settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Judge0 API settings
    judge0_api_url: Optional[str] = os.getenv("JUDGE0_API_URL")
    judge0_api_key: Optional[str] = os.getenv("JUDGE0_API_KEY")
    
    class Config:
        env_file = ".env"


settings = Settings()