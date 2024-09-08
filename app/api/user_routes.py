from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserCreate, User, UserLogin
from app.services.user_service import create_user, get_user, login_or_register
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=User)
async def create_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

@router.get("/{user_id}", response_model=User)
async def get_user_route(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user

@router.post("/login_or_register", response_model=User)
async def login_or_register_route(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_or_register(db, user)


@router.post("/check_story_completion")
async def check_story_completion_route():
    try:
        result = await llm_service.check_story_completion(request.story, request.messages)
        return {"is_complete": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查故事完整性时发生错误：{str(e)}")