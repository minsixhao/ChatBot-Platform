from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.chat import Chat, ChatModel, Message, MessageModel, MessageCreate, ChatCreate  # 添加 ChatCreate
from app.db.database import UserModel, BotModel
from datetime import datetime
from app.utils.id_generator import generate_ulid  # 从 id_generator 导入
import random
from fastapi import HTTPException
import logging
from app.models.enums import SenderType, MessageRole, ModelType
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

async def create_chat(db: AsyncSession, chat: ChatCreate):
    # 检查 creator_id 是否有效
    creator = await db.execute(select(UserModel).filter(UserModel.id == chat.creator_id))
    creator = creator.scalar_one_or_none()
    if not creator:
        logger.error(f"Invalid creator_id: {chat.creator_id}")
        raise HTTPException(status_code=400, detail="无效的创建者ID")
    
    logger.info(f"Creator found: {creator}")

    # 检查 bot_id 是否有效
    bot = await db.execute(select(BotModel).filter(BotModel.id == chat.bot_id))
    bot = bot.scalar_one_or_none()
    if not bot:
        logger.error(f"Invalid bot_id: {chat.bot_id}")
        raise HTTPException(status_code=400, detail="无效的机器人ID")
    
    logger.info(f"Bot found: {bot}")

    current_time = datetime.utcnow()
    db_chat = ChatModel(
        id=generate_ulid(),
        title=chat.title,
        creator_id=chat.creator_id,
        bot_id=chat.bot_id,
        created_at=current_time,
        updated_at=current_time
    )
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    logger.info(f"Chat created: {db_chat.id}")
    return db_chat

async def get_chat(db: AsyncSession, chat_id: str) -> Chat:
    result = await db.execute(select(ChatModel).filter(ChatModel.id == chat_id))
    db_chat = result.scalar_one_or_none()
    if db_chat:
        return Chat.model_validate(db_chat)
    return None

async def add_message(db: AsyncSession, chat_id: str, message: MessageCreate):
    try:
        print("==messagemessage:", message)
        if message.sender_type == SenderType.USER:  # 直接比较枚举
            user_query = select(UserModel).filter(UserModel.id == message.sender_id)
        elif message.sender_type == SenderType.BOT:  # 直接比较枚举
            user_query = select(BotModel).filter(BotModel.id == message.sender_id)
        else:
            raise ValueError("Invalid sender_type")

        sender = await db.execute(user_query)
        sender = sender.scalar_one_or_none()
        if not sender:
            raise HTTPException(status_code=404, detail=f"{message.sender_type.name.capitalize()} with ID {message.sender_id} not found")

        current_time = datetime.utcnow()
        print("===message:", message)
        db_message = MessageModel(
            id=generate_ulid(),
            chat_id=chat_id,
            sender_id=message.sender_id,
            sender_type=message.sender_type,
            content=message.content,
            role=message.role,
            created_at=current_time
        )
        print("==db_message:", db_message)
        db.add(db_message)
        
        # 更新聊天的 updated_at 字段
        await db.execute(
            update(ChatModel).where(ChatModel.id == chat_id).values(updated_at=current_time)
        )
        
        await db.commit()
        await db.refresh(db_message)
        logger.info(f"Message added successfully with id {db_message.id}")
        return Message.model_validate(db_message)
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        logger.exception("Detailed error information:")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"无法添加消息: {str(e)}")

async def get_chat_messages(db: AsyncSession, chat_id: str) -> list[Message]:
    result = await db.execute(select(MessageModel).filter(MessageModel.chat_id == chat_id))
    return [Message.model_validate(msg) for msg in result.scalars().all()]

async def get_bot_response(message: str, chat_id: str, bot_id: str, model_type: ModelType) -> str:
    llm_service = LLMService()
    
    try:
        response = await llm_service.generate_response(message, chat_id, bot_id, model_type)
        return response
    except Exception as e:
        logger.error(f"Error getting bot response: {str(e)}")
        return "抱歉,我现在无法回答。请稍后再试。"

async def chat_with_bot(db: AsyncSession, chat_id: str, user_message: MessageCreate) -> dict:
    try:
        # 获取聊天信息
        chat = await get_chat(db, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="聊天未找到")
        
        logger.info(f"Attempting to add message with sender_id: {user_message.sender_id}")

        # 确保用户消息包含 sender_type
        user_message.sender_type = SenderType.USER
        print("==user_message:", user_message)
        # 保存用户消息
        user_msg = await add_message(db, chat_id, user_message)
        print("==user_msg:", user_msg)

        # 获取LLM响应
        llm_response_content = await get_bot_response(user_message.content, chat_id, chat.bot_id, ModelType.GPT4O)
        print("==llm_response_content:", llm_response_content)
        
        # 创建并保存LLM响应
        llm_msg_create = MessageCreate(
            content=llm_response_content,
            sender_id=chat.bot_id,
            sender_type=SenderType.BOT,
            role=MessageRole.ASSISTANT
        )
        print("==llm_msg_create:", llm_msg_create)
        llm_msg = await add_message(db, chat_id, llm_msg_create)
        print("==llm_msg:", llm_msg)
        
        # 返回用户消息和LLM响应
        return {
            "user_message": user_msg.dict(),
            "llm_response": llm_msg.dict()
        }
    except Exception as e:
        logger.error(f"Error in chat_with_bot: {str(e)}")
        logger.exception("详细错误信息：")
        raise HTTPException(status_code=500, detail=f"处理聊天消息时发生错误: {str(e)}")