from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import UserCreate, User
from app.db.database import UserModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    print("====user:", user)
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(username=user.username, email=user.email, hashed_password=hashed_password)
    print("====db_user:", db_user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return User.model_validate(db_user)

async def get_user(db: AsyncSession, user_id: str) -> User:
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user:
        return User.model_validate(db_user)
    return None

async def get_user_by_username(db: AsyncSession, username: str) -> User:
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    db_user = result.scalar_one_or_none()
    if db_user:
        return User.model_validate(db_user)
    return None