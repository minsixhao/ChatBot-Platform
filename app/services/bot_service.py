from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.bot import BotCreate, Bot
from app.utils.database import BotModel

async def create_bot(db: AsyncSession, bot: BotCreate) -> Bot:
    db_bot = BotModel(**bot.model_dump())
    db.add(db_bot)
    await db.commit()
    await db.refresh(db_bot)
    return Bot.model_validate(db_bot)

async def get_bot(db: AsyncSession, bot_id: str) -> Bot:
    result = await db.execute(select(BotModel).filter(BotModel.id == bot_id))
    db_bot = result.scalar_one_or_none()
    if db_bot:
        return Bot.model_validate(db_bot)
    return None