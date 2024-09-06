from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bot import BotCreate, Bot
from app.services.bot_service import create_bot, get_bot
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=Bot)
async def create_bot_route(bot: BotCreate, db: AsyncSession = Depends(get_db)):
    return await create_bot(db, bot)

@router.get("/{bot_id}", response_model=Bot)
async def get_bot_route(bot_id: str, db: AsyncSession = Depends(get_db)):
    bot = await get_bot(db, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot