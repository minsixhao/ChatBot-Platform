from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from .enums import SenderType, MessageRole  # 确保这行正确导入
from app.models.orm import Base
from ulid import ULID
from .schemas import MessageCreate  # 添加这行

# 删除这一行
# from app.db.database import Base, Column, String, DateTime, ForeignKey, Boolean

# 如果需要使用这些类型，可以从 sqlalchemy 直接导入
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean

# 如果需要 Base 类，从 orm.py 导入
from app.models.orm import Base

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BotBase(BaseModel):
    name: str
    description: str

class BotCreate(BotBase):
    creator_id: str

class Bot(BotBase):
    id: str
    creator_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageBase(BaseModel):
    role: MessageRole
    content: str

class Message(MessageBase):
    id: str = Field(max_length=30)
    chat_id: str = Field(max_length=30)
    sender_id: str
    sender_type: SenderType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatBase(BaseModel):
    title: str

class ChatCreate(BaseModel):
    title: str
    chat_type: ChatType
    creator_id: str
    user_ids: List[str] = []
    bot_ids: List[str] = []

class Chat(ChatBase):
    id: str
    creator_id: str
    bot_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# SQLAlchemy models
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BotModel(Base):
    __tablename__ = "bots"

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    creator_id = Column(String, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ChatModel(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True)
    title = Column(String)
    creator_id = Column(String, ForeignKey("users.id"))
    bot_id = Column(String, ForeignKey("bots.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    chat_id = Column(String(26), ForeignKey("chats.id"))
    sender_id = Column(String(26))
    sender_type = Column(SQLAlchemyEnum(SenderType))  # 修改这行
    role = Column(SQLAlchemyEnum(MessageRole))  # 修改这行
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic模型用于API交互
class ChatPydantic(BaseModel):
    id: str
    title: str
    creator_id: str
    bot_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessagePydantic(BaseModel):
    id: str
    role: MessageRole
    content: str
    sender_id: str
    chat_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)