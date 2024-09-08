from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.chat_service import ChatService
from app.services.bot_service import BotService
from app.models.schemas import ChatCreate, Chat, MessageCreate, Message
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_chat_service(db: AsyncSession = Depends(get_db)):
    bot_service = BotService(db)
    return ChatService(db, bot_service)

@router.post("/", response_model=Chat)
async def create_chat(chat: ChatCreate, chat_service: ChatService = Depends(get_chat_service)):
    return await chat_service.create_chat(chat)

@router.get("/all", response_model=List[Chat])
async def get_all_chats(chat_service: ChatService = Depends(get_chat_service)):
    return await chat_service.get_all_chats()

@router.get("/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str, chat_service: ChatService = Depends(get_chat_service)):
    print(f"尝试获取聊天ID: {chat_id}")
    try:
        chat = await chat_service.get_chat(chat_id)
        if not chat:
            print(f"未找到聊天ID: {chat_id}")
            raise HTTPException(status_code=404, detail="聊天未找到")
        print(f"成功获取聊天ID: {chat_id}")
        return chat
    except Exception as e:
        print(f"获取聊天时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取聊天时发生错误: {str(e)}")

@router.get("/users/{user_id}", response_model=List[Chat])
async def get_chat_history(user_id: str, limit: int = 10, chat_service: ChatService = Depends(get_chat_service)):
    return await chat_service.get_chat_history(user_id, limit)

# 添加消息到聊天
@router.post("/{chat_id}/messages", response_model=List[Message])
async def add_message_to_chat(
    chat_id: str,
    message: MessageCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        messages = await chat_service.add_message_and_get_caipan_reply(chat_id, message)
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/join/{chat_id}/user/{user_id}", response_model=Chat)
async def add_user_to_chat(chat_id: str, user_id: str, chat_service: ChatService = Depends(get_chat_service)):
    print(f"API: 尝试将用户 {user_id} 添加到聊天 {chat_id}")
    try:
        result = await chat_service.add_user_to_chat(chat_id, user_id)
        print("API: 用户成功添加到聊天")
        return result
    except ValueError as e:
        print(f"API: 值错误 - {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"API: 未知错误 - {str(e)}")
        raise HTTPException(status_code=500, detail=f"发生未知错误: {str(e)}")

@router.delete("/{chat_id}/user/{user_id}", response_model=Chat)
async def remove_user_from_chat(chat_id: str, user_id: str, chat_service: ChatService = Depends(get_chat_service)):
    try:
        return await chat_service.remove_user_from_chat(chat_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{chat_id}/messages/history", response_model=List[Message])
async def get_chat_messages_history(chat_id: str, limit: int = 50, chat_service: ChatService = Depends(get_chat_service)):
    try:
        messages = await chat_service.get_chat_messages_history(chat_id, limit)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))