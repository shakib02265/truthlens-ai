import os
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "TruthLens AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Security
    SECRET_KEY: str = Field(default="truthlens_super_secret_jwt_key_change_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database (Workspace root absolute path)
    DATABASE_URL: str = Field(
        default=f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'truthlens.db').replace('\\', '/')}"
    )
    
    # Mode
    DEMO_MODE: bool = Field(default=True)

    # LLM Configuration
    LLM_PROVIDER: str = Field(default="demo")  # demo, openai, gemini, anthropic
    LLM_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)

    # Search Configuration
    SEARCH_PROVIDER: str = Field(default="demo")  # demo, tavily, serper, google
    TAVILY_API_KEY: Optional[str] = Field(default=None)
    SERPER_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_SEARCH_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = Field(default=None)

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*",
    ]

    # Confidence Engine Weights
    CONFIDENCE_WEIGHT_SOURCE_QUALITY: float = 0.30
    CONFIDENCE_WEIGHT_EVIDENCE_AGREEMENT: float = 0.25
    CONFIDENCE_WEIGHT_EVIDENCE_STRENGTH: float = 0.20
    CONFIDENCE_WEIGHT_RECENCY: float = 0.10
    CONFIDENCE_WEIGHT_INDEPENDENT_SOURCES: float = 0.10
    CONFIDENCE_WEIGHT_CONTRADICTION_PENALTY: float = 0.05

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
