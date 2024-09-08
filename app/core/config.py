from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://mins:mins@localhost/hgt"  # 修改这行
    SECRET_KEY: str = "default_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEEPSEEK_API_KEY: str
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

# 为了向后兼容，我们可以直接暴露 DATABASE_URL
DATABASE_URL = settings.DATABASE_URL