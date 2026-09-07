import os
from typing import Dict, List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "SIH26100 - GeM Bid Compliance Verification Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment & Database
    ENV: str = "development"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'app.db').replace(chr(92), '/')}"
    )
    
    # Security / Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "sih26100-gem-procurement-compliance-secret-key-2026"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    @property
    def SECRET_KEY(self) -> str:
        return self.JWT_SECRET
        
    @property
    def ALGORITHM(self) -> str:
        return self.JWT_ALGORITHM
    
    # Storage
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
    )
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
    
    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Scoring Configuration (Total equals 100%)
    SCORING_WEIGHTS: Dict[str, float] = {
        "STATUTORY": 0.30,      # GST, PAN, Udyam, EPFO, ESIC, Blacklist
        "FINANCIAL": 0.25,      # Turnover, Net worth, Solvency
        "TENDER_SPECIFIC": 0.20,# OEM Auth, Local Content / Make in India, Experience
        "DOCUMENTATION": 0.15,  # Mandatory certificates, signatures, completeness
        "OTHER_ELIGIBILITY": 0.10 # Startup India, NSIC, ISO
    }
    
    # AI / Confidence Gating Thresholds
    CONFIDENCE_HIGH: float = 0.90      # Auto-accepted if rule matches
    CONFIDENCE_MEDIUM: float = 0.70    # Review recommended
    
    # NVIDIA NIM LLM & Vision Configuration
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "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")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.2-90b-vision-instruct")
    NVIDIA_INVOKE_URL: str = os.getenv("NVIDIA_INVOKE_URL", "https://integrate.api.nvidia.com/v1/chat/completions")

    # Adapter Settings
    USE_MOCK_PORTALS: bool = True
    GOVERNMENT_SOURCE_LABEL: str = "DEMO / MOCK GOVERNMENT SOURCE"

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
