import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

def load_dotenv(dotenv_path: Path):
    """Simple, lightweight .env parser loading variables into os.environ"""
    if not dotenv_path.exists():
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'").strip('"')
            if key not in os.environ:
                os.environ[key] = val

# Load .env file if present
load_dotenv(BASE_DIR.parent / ".env")

class Settings:
    """Centralized Environment & Secret Management Configuration"""
    
    APP_NAME: str = os.getenv("APP_NAME", "Prashanth Hospitals Call Center & SLM Platform")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ph-callcenter-secret-key-change-in-production")

    # JWT Auth — default admin account is seeded on first boot only (see
    # main.init_db). Override these in .env for any real deployment.
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "hxyE7C!roFnMGIsaH1xT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    
    # Database Configuration & Pool Parameters
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://ph_db_user:ph_secure_pass@localhost:5432/ph_callcenter_slm_db"
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    
    # XTEND DB2 Integration Credentials
    XTEND_DB2_HOST: str = os.getenv("XTEND_DB2_HOST", "192.168.1.100")
    XTEND_DB2_PORT: int = int(os.getenv("XTEND_DB2_PORT", "50000"))
    XTEND_DB2_USER: str = os.getenv("XTEND_DB2_USER", "xtend_sync_user")
    XTEND_DB2_PASSWORD: str = os.getenv("XTEND_DB2_PASSWORD", "xtend_secure_pass")
    XTEND_DB2_DATABASE: str = os.getenv("XTEND_DB2_DATABASE", "XTENDDB2")
    
    # FCM (Firebase Cloud Messaging) Push Credentials
    FCM_SERVER_KEY: str = os.getenv("FCM_SERVER_KEY", "fcm_server_key_placeholder")
    FCM_PROJECT_ID: str = os.getenv("FCM_PROJECT_ID", "prashanth-hospitals-slm")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    ]

settings = Settings()
