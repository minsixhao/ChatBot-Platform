from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm import UserModel
from app.models.schemas import User, UserCreate
from typing import Optional
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_user(self, user: UserCreate) -> User:
        hashed_password = self.get_password_hash(user.password)
        db_user = UserModel(username=user.username, email=user.email, hashed_password=hashed_password)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return User.from_orm(db_user)

    async def get_user(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(UserModel).filter(UserModel.id == user_id))
        db_user = result.scalar_one_or_none()
        return User.from_orm(db_user) if db_user else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(UserModel).filter(UserModel.username == username))
        db_user = result.scalar_one_or_none()
        return User.from_orm(db_user) if db_user else None