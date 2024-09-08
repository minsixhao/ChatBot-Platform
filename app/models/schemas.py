from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.models.enums import SenderType, MessageRole, ModelType, ChatType

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    id: str
    username: str
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

class UserInDB(User):
    hashed_password: str

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

class MessageCreate(BaseModel):
    content: str
    role: MessageRole
    sender_id: str
    sender_type: SenderType

class Message(MessageBase):
    id: str = Field(max_length=30)
    chat_id: str = Field(max_length=30)
    sender_id: str
    sender_type: SenderType
    created_at: datetime
    group_chat_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ChatBase(BaseModel):
    title: str
    chat_type: ChatType

class ChatCreate(BaseModel):
    title: str
    creator_id: str
    chat_type: ChatType = Field(default=ChatType.SINGLE)
    user_ids: List[str] = Field(default_factory=list)
    bot_ids: List[str] = Field(default_factory=list)

class HaiguiTang(BaseModel):
    id: str
    title: str
    tang_mian: Optional[str]
    tang_di: Optional[str]
    tags: List[str]
    usage_count: int
    difficulty: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatHaiguiTangHistory(BaseModel):
    id: str
    chat_id: str
    haiguitang_id: str
    start_time: datetime
    end_time: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class Chat(BaseModel):
    id: str
    title: str
    chat_type: ChatType
    creator_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    users: List[User]
    bots: List[Bot]
    messages: Optional[List[Message]] = None
    last_message: Optional[Message] = None
    current_haiguitang_id: Optional[str] = None
    current_haiguitang: Optional[HaiguiTang] = None
    haiguitang_history: List[ChatHaiguiTangHistory] = []

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class ChatResponse(BaseModel):
    id: str
    title: str
    chat_type: str
    creator_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    users: List['User']
    bots: List['Bot']
    messages: Optional[List['Message']] = None
    last_message: Optional['Message'] = None
    current_haiguitang_id: Optional[str] = None
    current_haiguitang: Optional['HaiguiTang'] = None
    haiguitang_history: List['HaiguiTang'] = []

    class Config:
        from_attributes = True

ChatResponse.update_forward_refs()