from app.repositories.chat_repository import ChatRepository
from app.services.bot_service import BotService
from app.models.schemas import Chat, ChatCreate, MessageCreate, Message
from app.models.enums import MessageRole, SenderType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import List
import logging
import asyncio
from app.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: AsyncSession, bot_service: BotService):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.bot_service = bot_service

    async def create_chat(self, chat: ChatCreate) -> Chat:
        # 确保这里设置了current_haiguitang
        db_chat = await self.chat_repository.create_chat(chat)
        # 如果需要，在这里设置initial_haiguitang
        # db_chat.current_haiguitang = initial_haiguitang
        # await self.chat_repository.update(db_chat)
        return await self.chat_repository.chat_to_schema(db_chat)

    async def get_chat(self, chat_id: str):
        logger.info(f"ChatService: 尝试获取聊天ID: {chat_id}")
        try:
            chat = await self.chat_repository.get_chat(chat_id)
            if chat:
                logger.info(f"ChatService: 成功获取聊天ID: {chat_id}")
                logger.info(f"ChatService: current_haiguitang_id: {chat.current_haiguitang_id}")
                logger.info(f"ChatService: current_haiguitang: {chat.current_haiguitang}")
                # 获取聊天历史记录
                chat.messages = await self.get_chat_messages_history(chat_id)
            else:
                logger.warning(f"ChatService: 未找到天ID: {chat_id}")
            return chat
        except Exception as e:
            logger.error(f"ChatService: 获取聊天时发生错误: {str(e)}")
            raise

    async def get_chat_history(self, user_id: str, limit: int = 10) -> List[Chat]:
        return await self.chat_repository.get_chat_history(user_id, limit)

    async def add_message_and_get_caipan_reply(self, chat_id: str, message: MessageCreate) -> List[Message]:
        chat = await self.chat_repository.get_chat(chat_id)
        if not chat:
            raise ValueError(f"Chat with id {chat_id} not found")

        user_message = await self.chat_repository.add_message(chat_id, message)

        chat_history = await self.chat_repository.get_chat_messages_history(chat_id)

        caipan_bot = next((bot for bot in chat.bots if bot.id == 'caipan'), None)
        if not caipan_bot:
            raise ValueError("在聊天中找不到'caipan'机器人")
        bot_id = caipan_bot.id

        bot_reply = await self.bot_service.generate_chat_message_response(chat_history, chat_id, caipan_bot.id)

        bot_message = MessageCreate(
            content=bot_reply,
            role=MessageRole.ASSISTANT,
            sender_id=bot_id,
            sender_type=SenderType.BOT
        )
        bot_message = await self.chat_repository.add_message(chat_id, bot_message)

        messages = [user_message, bot_message]

        # 检查是否需要 验证故事完成度
        print(f"================ChatService: 当前消息: {bot_message}")
        is_handle_story_completion = bot_message.role == MessageRole.ASSISTANT and bot_message.content.strip().lower().startswith("是")

        print(f"================ChatService: 当前消息: {is_handle_story_completion}")
        if is_handle_story_completion:
            # chat 在什么情况下插入海龟汤呢？！！！
            # 获取当前的海龟汤汤底
            print(f"================ChatService: 当前海龟汤汤底: {chat.current_haiguitang}")
            tang_di = chat.current_haiguitang.tang_di

            messages = await self.bot_service.handle_story_completion(chat_id, tang_di, messages)

        return messages

    async def add_user_to_chat(self, chat_id: str, user_id: str) -> Chat:
        return await self.chat_repository.add_user_to_chat(chat_id, user_id)

    async def remove_user_from_chat(self, chat_id: str, user_id: str) -> Chat:
        return await self.chat_repository.remove_user_from_chat(chat_id, user_id)

    async def get_all_chats(self) -> List[Chat]:
        logger.info("ChatService: 尝试获取所有聊天")
        try:
            chats = await self.chat_repository.get_all_chats()
            logger.info(f"ChatService: 成功获取所有聊天，共 {len(chats)} 条记录")
            return chats
        except Exception as e:
            logger.error(f"ChatService: 获取所有聊天时发生错误: {str(e)}")
            raise

    async def get_chat_messages_history(self, chat_id: str, limit: int = 50) -> List[Message]:
        logger.info(f"ChatService: 尝试获取聊天ID {chat_id} 的消息历史")
        try:
            messages = await self.chat_repository.get_chat_messages_history(chat_id, limit)
            logger.info(f"ChatService: 成功获取聊天ID {chat_id} 的消息历史，共 {len(messages)} 条消息")
            return messages
        except Exception as e:
            logger.error(f"ChatService: 获取聊天消息历史时发生错误: {str(e)}")
            raise

    async def get_chat_messages(self, chat_id: str) -> List[Message]:
        try:
            messages = await self.chat_repository.get_chat_messages(chat_id)
            return messages
        except Exception as e:
            logger.error(f"ChatService: 获取聊天消息历史时发生错误: {str(e)}")
            raise
