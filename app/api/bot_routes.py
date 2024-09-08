from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import BotCreate, Bot
from app.services.bot_service import BotService
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=Bot)
async def create_bot_route(bot: BotCreate, db: AsyncSession = Depends(get_db)):
    bot_service = BotService(db)
    return await bot_service.create_bot(bot)

@router.get("/{bot_id}", response_model=Bot)
async def get_bot_route(bot_id: str, db: AsyncSession = Depends(get_db)):
    bot_service = BotService(db)
    bot = await bot_service.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

# @router.post("/check_story_completion")
# async def check_story_completion_route(
#     request: StoryCompletionRequest,
#     llm_service: LLMService = Depends(LLMService)
# ):
#     try:
#         result = await llm_service.check_story_completion(request.story, request.messages)
#         return {"is_complete": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"检查故事完整性时发生错误：{str(e)}")