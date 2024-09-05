from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

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

class ChatBase(BaseModel):
    title: str

class ChatCreate(ChatBase):
    creator_id: str
    bot_id: str

class Chat(ChatBase):
    id: str
    creator_id: str
    bot_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageBase(BaseModel):
    content: str
    sender_id: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str
    chat_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)