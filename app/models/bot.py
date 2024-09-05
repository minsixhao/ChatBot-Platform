from pydantic import BaseModel, ConfigDict
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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None