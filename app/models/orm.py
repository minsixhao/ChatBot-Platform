from sqlalchemy import Table, Column, String, DateTime, Boolean, ForeignKey, Enum as SQLAlchemyEnum, Integer, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from app.models.enums import SenderType, MessageRole, ChatType
from ulid import ULID
from sqlalchemy.sql import func

Base = declarative_base()

chat_users = Table('chat_users', Base.metadata,
    Column('chat_id', String(26), ForeignKey('chats.id')),
    Column('user_id', String(26), ForeignKey('users.id'))
)

chat_bots = Table('chat_bots', Base.metadata,
    Column('chat_id', String(26), ForeignKey('chats.id')),
    Column('bot_id', String(26), ForeignKey('bots.id'))
)

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chats = relationship("ChatModel", secondary=chat_users, back_populates="users")

class BotModel(Base):
    __tablename__ = "bots"
    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    name = Column(String, index=True)
    description = Column(String)
    creator_id = Column(String(26), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chats = relationship("ChatModel", secondary=chat_bots, back_populates="bots")

class ChatModel(Base):
    __tablename__ = "chats"
    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    title = Column(String, index=True)
    chat_type = Column(SQLAlchemyEnum(ChatType, native_enum=False), nullable=False, server_default=ChatType.SINGLE.value)
    creator_id = Column(String(26), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    current_haiguitang_id = Column(String(26), ForeignKey("haiguitang.id"), nullable=True)  # 新增：当前使用的海龟汤ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("UserModel", secondary=chat_users, back_populates="chats")
    bots = relationship("BotModel", secondary=chat_bots, back_populates="chats")
    messages = relationship("MessageModel", back_populates="chat")
    current_haiguitang = relationship("HaiguiTangModel")  # 新增：与当前海龟汤的关系
    haiguitang_history = relationship("ChatHaiguiTangHistory", back_populates="chat")  # 新增：与历史记录的关系

class MessageModel(Base):
    __tablename__ = "messages"
    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    chat_id = Column(String(26), ForeignKey("chats.id"))
    sender_id = Column(String(26))
    sender_type = Column(SQLAlchemyEnum(SenderType))
    role = Column(SQLAlchemyEnum(MessageRole))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("ChatModel", back_populates="messages")

class HaiguiTangModel(Base):
    __tablename__ = "haiguitang"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    title = Column(String, nullable=False)  # 标题
    tang_mian = Column(String, nullable=True)  # 汤面
    tang_di = Column(String, nullable=True)  # 汤底
    tags = Column(ARRAY(String))  # 标签
    usage_count = Column(Integer, default=0)  # 使用次数
    difficulty = Column(Integer)  # 难度等级
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ChatHaiguiTangHistory(Base):
    __tablename__ = "chat_haiguitang_history"
    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    chat_id = Column(String(26), ForeignKey("chats.id"), nullable=False)
    haiguitang_id = Column(String(26), ForeignKey("haiguitang.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    chat = relationship("ChatModel", back_populates="haiguitang_history")
    haiguitang = relationship("HaiguiTangModel")