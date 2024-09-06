from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat, ChatCreate, Message, MessageCreate
from app.services.chat_service import create_chat, get_chat, add_message, get_chat_messages, chat_with_bot
from app.db.database import get_db  # 修改这一行

router = APIRouter()

@router.post("/", response_model=Chat)
async def create_chat_route(chat: ChatCreate, db: AsyncSession = Depends(get_db)):
    return await create_chat(db, chat)

@router.get("/{chat_id}", response_model=Chat)
async def get_chat_route(chat_id: str, db: AsyncSession = Depends(get_db)):
    chat = await get_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="聊天未找到")
    return chat

@router.post("/{chat_id}/messages/", response_model=dict)
async def add_message_route(chat_id: str, message: MessageCreate, db: AsyncSession = Depends(get_db)):
    try:
        if not hasattr(message, 'sender_type'):
           message.sender_type = "user"
        print("========message:", message)
        result = await chat_with_bot(db, chat_id, message)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{chat_id}/messages/", response_model=list[Message])
async def get_chat_messages_route(chat_id: str, db: AsyncSession = Depends(get_db)):
    messages = await get_chat_messages(db, chat_id)
    if not messages:
        raise HTTPException(status_code=404, detail="聊天消息未找到")
    return messages

# @router.post("/{chat_id}/chat_with_llm/", response_model=Message)
# async def chat_with_llm_route(chat_id: str, message: MessageCreate, db: AsyncSession = Depends(get_db)):
#     return await chat_with_llm(db, chat_id, message)