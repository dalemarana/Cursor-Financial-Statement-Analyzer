"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database - Default to SQLite for development
    database_url: str = "sqlite:///./financial_analyzer.db"
    
    # JWT Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Environment
    environment: str = "development"
    
    # Parser Settings
    use_github_parser: bool = True  # Use GitHub parser as primary parser
    github_parser_fallback: bool = True  # Fall back to new parser if GitHub parser fails
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

