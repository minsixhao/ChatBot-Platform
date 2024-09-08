from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm import BotModel
from app.models.schemas import Bot, BotCreate
from typing import Optional
from datetime import datetime

class BotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_bot(self, bot: BotCreate) -> Bot:
        db_bot = BotModel(**bot.dict(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        self.db.add(db_bot)
        await self.db.commit()
        await self.db.refresh(db_bot)
        return Bot.from_orm(db_bot)

    async def get_bot(self, bot_id: str) -> Optional[Bot]:
        result = await self.db.execute(select(BotModel).filter(BotModel.id == bot_id))
        db_bot = result.scalar_one_or_none()
        return Bot.from_orm(db_bot) if db_bot else None