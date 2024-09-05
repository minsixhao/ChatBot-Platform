from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chat import Chat, ChatCreate, Message, MessageCreate
from app.utils.database import ChatModel, MessageModel, UserModel
import random

async def create_chat(db: AsyncSession, chat: ChatCreate) -> Chat:
    db_chat = ChatModel(title=chat.title, creator_id=chat.creator_id, bot_id=chat.bot_id)
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    return Chat.model_validate(db_chat)

async def get_chat(db: AsyncSession, chat_id: str) -> Chat:
    result = await db.execute(select(ChatModel).filter(ChatModel.id == chat_id))
    db_chat = result.scalar_one_or_none()
    if db_chat:
        return Chat.model_validate(db_chat)
    return None

async def add_message(db: AsyncSession, chat_id: str, message: MessageCreate) -> Message:
    db_message = MessageModel(chat_id=chat_id, **message.model_dump())
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return Message.model_validate(db_message)

async def get_chat_messages(db: AsyncSession, chat_id: str) -> list[Message]:
    result = await db.execute(select(MessageModel).filter(MessageModel.chat_id == chat_id))
    return [Message.model_validate(msg) for msg in result.scalars().all()]

async def get_llm_response(message: str) -> str:
    responses = [
        "这是一个有趣的话题。",
        "我明白你的观点。",
        "你能详细解释一下吗？",
        "这让我想到了...",
        "我需要更多信息来回答这个问题。"
    ]
    return random.choice(responses)

async def chat_with_llm(db: AsyncSession, chat_id: str, user_message: MessageCreate) -> Message:
    # 获取聊天信息
    chat = await get_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="聊天未找到")

    # 保存用户消息
    user_msg = await add_message(db, chat_id, user_message)
    
    # 获取LLM响应
    llm_response_content = await get_llm_response(user_message.content)
    
    # 创建并保存LLM响应
    llm_message = MessageCreate(content=llm_response_content, sender_id=chat.bot_id)
    llm_msg = await add_message(db, chat_id, llm_message)
    
    return llm_msg