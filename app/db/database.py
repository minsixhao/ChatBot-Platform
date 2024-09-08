from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        # 这里可以添加初始化数据库的逻辑
        pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def drop_all_tables():
    async with engine.begin() as conn:
        # 这里可以添加删除所有表的逻辑
        pass

# 确保这些函数被导出
__all__ = ["init_db", "get_db", "drop_all_tables"]