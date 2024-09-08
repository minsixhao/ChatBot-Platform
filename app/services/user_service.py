from app.models.orm import UserModel
from app.models.schemas import UserCreate, User, UserLogin, UserInDB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import uuid
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查电子邮件是否已存在
    if user.email:
        existing_email = await get_user_by_email(db, user.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="电子邮件已被使用")

    db_user = UserModel(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        email=user.email if user.email else None
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return User.model_validate(db_user)

async def login_user(db: AsyncSession, user: UserLogin) -> User:
    db_user = await get_user_by_username(db, user.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return User.model_validate(db_user)

async def login_or_register(db: AsyncSession, user: UserLogin) -> User:
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        return await login_user(db, user)
    else:
        new_user = UserCreate(username=user.username, password=user.password)
        return await create_user(db, new_user)

async def get_user(db: AsyncSession, user_id: str) -> User:
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user:
        return User.model_validate(db_user)
    return None

async def get_user_by_username(db: AsyncSession, username: str) -> UserInDB | None:
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    db_user = result.scalar_one_or_none()
    if db_user:
        return UserInDB.model_validate(db_user)
    return None

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(UserModel).filter(UserModel.email == email))
    db_user = result.scalar_one_or_none()
    if db_user:
        return User.model_validate(db_user)
    return None