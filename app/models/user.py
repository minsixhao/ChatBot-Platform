from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr | None = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserInDB(User):
    hashed_password: str

class UserLogin(BaseModel):
    username: str
    password: str