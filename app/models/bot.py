from pydantic import BaseModel, ConfigDict, Field, validator
from datetime import datetime
from typing import Optional

class BotBase(BaseModel):
    name: str
    description: str

class BotCreate(BotBase):
    creator_id: str

class Bot(BotBase):
    id: str
    creator_id: str
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)

    @validator('created_at', 'updated_at', pre=True)
    def set_datetime(cls, v):
        if v is None:
            return datetime.utcnow()
        return v

class BotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None