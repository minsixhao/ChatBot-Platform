from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.enums import SenderType, MessageRole
from datetime import datetime
from ulid import ULID

class ChatModel(Base):
    __tablename__ = "chats"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    title = Column(String)
    creator_id = Column(String(26), ForeignKey("users.id"))
    bot_id = Column(String(26), ForeignKey("bots.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    chat_id = Column(String(26), ForeignKey("chats.id"))
    sender_id = Column(String(26))
    sender_type = Column(SQLAlchemyEnum(SenderType))
    role = Column(SQLAlchemyEnum(MessageRole))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)