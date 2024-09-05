from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from ulid import ULID

DATABASE_URL = "postgresql+asyncpg://mins:mins@localhost/hgt"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotModel(Base):
    __tablename__ = "bots"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    name = Column(String, index=True)
    description = Column(String)
    creator_id = Column(String(26), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatModel(Base):
    __tablename__ = "chats"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    title = Column(String, index=True)
    creator_id = Column(String(26), ForeignKey("users.id"))
    bot_id = Column(String(26), ForeignKey("bots.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    chat_id = Column(String(26), ForeignKey("chats.id"))
    sender_id = Column(String(26), ForeignKey("users.id"))  # 可以是用户ID或bot ID
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

__all__ = ["init_db", "get_db", "UserModel", "BotModel", "ChatModel", "MessageModel", "drop_all_tables"]