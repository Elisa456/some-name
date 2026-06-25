import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Добавлено
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@green-landscape.ru")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
