from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from sqlalchemy.orm import relationship

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserInDB(User):
    hashed_password: str