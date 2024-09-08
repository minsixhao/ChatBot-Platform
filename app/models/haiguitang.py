from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.orm import HaiguiTangModel  # 新增这行

class HaiguiTangBase(BaseModel):
    title: str
    tang_mian: Optional[str] = None
    tang_di: Optional[str] = None
    tags: List[str]
    difficulty: int

class HaiguiTangCreate(HaiguiTangBase):
    pass

class HaiguiTang(HaiguiTangBase):
    id: str
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HaiguiTangUpdate(BaseModel):
    title: Optional[str] = None
    tang_mian: Optional[str] = None
    tang_di: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: Optional[int] = None