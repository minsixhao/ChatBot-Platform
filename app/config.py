from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional

# 加载 .env 文件
load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# 验证设置
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 未设置")