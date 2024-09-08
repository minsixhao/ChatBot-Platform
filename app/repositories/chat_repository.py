from app.models.enums import MessageRole, SenderType
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload, sessionmaker
from app.models.orm import ChatModel, UserModel, BotModel, MessageModel, HaiguiTangModel
from app.models.schemas import ChatResponse, Chat, Message, MessageCreate, ChatCreate, User, Bot, HaiguiTang
from typing import Optional, List
from app.services.bot_service import BotService
import logging
import asyncio
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def chat_to_schema(self, db_chat: ChatModel, include_messages: bool = False) -> ChatResponse:
        async with self.db as session:
            # 重新加载 db_chat 对象，包括所有需要的关系
            db_chat = await session.merge(db_chat)
            await session.refresh(db_chat, ['users', 'bots', 'current_haiguitang'])

            users = [await self.user_to_schema(user) for user in db_chat.users]
            bots = [Bot.model_validate(bot) for bot in db_chat.bots]
            
            last_message = None
            messages = None
            if include_messages:
                messages = [Message.model_validate(msg) for msg in db_chat.messages]
                if messages:
                    last_message = messages[-1]
            else:
                last_message = await self.get_last_message(db_chat.id)
            
            current_haiguitang = None
            if db_chat.current_haiguitang:
                current_haiguitang = HaiguiTang.model_validate(db_chat.current_haiguitang)
            
            return ChatResponse(
                id=db_chat.id,
                title=db_chat.title,
                chat_type=db_chat.chat_type,
                creator_id=db_chat.creator_id,
                is_active=db_chat.is_active,
                created_at=db_chat.created_at,
                updated_at=db_chat.updated_at,
                users=users,
                bots=bots,
                messages=messages,
                last_message=last_message,
                current_haiguitang_id=db_chat.current_haiguitang_id,
                current_haiguitang=current_haiguitang,
                haiguitang_history=[]  # 不查询海龟汤历史记录
            )

    async def user_to_schema(self, user: UserModel) -> User:
        return User(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def get_chat(self, chat_id: str, include_messages: bool = False) -> Optional[Chat]:
        async with self.db as session:
            query = select(ChatModel).options(
                selectinload(ChatModel.users),
                selectinload(ChatModel.bots),
                selectinload(ChatModel.current_haiguitang)
            )
            if include_messages:
                query = query.options(selectinload(ChatModel.messages))
            query = query.where(ChatModel.id == chat_id)
            
            result = await session.execute(query)
            db_chat = result.scalar_one_or_none()
            
            if db_chat:
                return await self.chat_to_schema(db_chat, include_messages)
            return None

    async def add_message(self, chat_id: str, message: MessageCreate) -> Message:
        async with self.db as session:
            async with session.begin():
                message_data = message.dict()
                db_message = MessageModel(**message_data, chat_id=chat_id)
                session.add(db_message)
            await session.refresh(db_message)
            return Message.from_orm(db_message)

    async def get_chat_messages_history(self, chat_id: str, limit: int = 50) -> List[Message]:
        async with self.db as session:  # 使用 self.db 而不是 self.db.begin()
            result = await session.execute(
                select(MessageModel).where(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at.desc()).limit(limit)
            )
            messages = result.scalars().all()
            return [Message.from_orm(msg) for msg in reversed(messages)]

    async def get_chat_history(self, user_id: str, limit: int = 10) -> List[Chat]:
        async with self.db as session:
            query = select(ChatModel).options(
                selectinload(ChatModel.users),
                selectinload(ChatModel.bots)
            ).filter(ChatModel.creator_id == user_id).order_by(ChatModel.created_at.desc()).limit(limit)
            result = await session.execute(query)
            db_chats = result.scalars().all()
            return [await self.chat_to_schema(chat) for chat in db_chats]

    async def create_chat(self, chat: ChatCreate) -> ChatModel:
        async with self.db as session:
            async with session.begin():
                chat_data = chat.dict(exclude={"user_ids", "bot_ids"})
                db_chat = ChatModel(**chat_data)
                
                # 添加创建者作为默认用户
                user_ids = {chat.creator_id}
                
                # 加用户
                users_query = select(UserModel).filter(UserModel.id.in_(user_ids))
                users_result = await session.execute(users_query)
                db_chat.users = list(users_result.scalars().all())
                
                # 加默认机器人'caipan'
                bot_ids = {'caipan'}
                
                # 添加机器人
                bots_query = select(BotModel).filter(BotModel.id.in_(bot_ids))
                bots_result = await session.execute(bots_query)
                db_chat.bots = list(bots_result.scalars().all())
                
                session.add(db_chat)
            
            # 在事务结束后刷新 db_chat 对象，包括 current_haiguitang
            await session.refresh(db_chat, attribute_names=['users', 'bots', 'current_haiguitang'])
            
            # 验证关联是否成功
            print(f"Chat users: {[user.id for user in db_chat.users]}")
            print(f"Chat bots: {[bot.id for bot in db_chat.bots]}")
            
            return db_chat

    async def get_last_message(self, chat_id: str) -> Optional[MessageModel]:
        async with self.db as session:
            query = select(MessageModel).filter(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at.desc()).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def add_user_to_chat(self, chat_id: str, user_id: str) -> Chat:
        print(f"Repository: 尝试将用户 {user_id} 添加到聊天 {chat_id}")
        
        async with self.db as session:
            async with session.begin():
                chat_query = select(ChatModel).options(
                    selectinload(ChatModel.users),
                    selectinload(ChatModel.bots),
                    selectinload(ChatModel.current_haiguitang)  # 添加这行来预加载 current_haiguitang
                ).filter(ChatModel.id == chat_id)
                result = await session.execute(chat_query)
                db_chat = result.scalar_one_or_none()
                
                if not db_chat:
                    print(f"Repository: 聊天 {chat_id} 不存在")
                    raise ValueError(f"聊天 {chat_id} 不存在")

                user_query = select(UserModel).filter(UserModel.id == user_id)
                result = await session.execute(user_query)
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    print(f"Repository: 用户 {user_id} 不存在")
                    raise ValueError(f"用户 {user_id} 不存在")

                print(f"Repository: 聊天和用户都存在，尝试添加用户到聊天")
                if db_user not in db_chat.users:
                    db_chat.users.append(db_user)
                    print(f"Repository: 用户成功添加到聊天")
                else:
                    print(f"Repository: 用户已经在聊天中")

            # 在事务结束后刷新 db_chat 对象
            await session.refresh(db_chat, ['users', 'bots', 'current_haiguitang'])
            
            # 使用刷新后的 db_chat 对象创建 schema
            return await self.chat_to_schema(db_chat)

    async def remove_user_from_chat(self, chat_id: str, user_id: str) -> Chat:
        async with self.db as session:
            async with session.begin():
                chat_query = select(ChatModel).options(
                    selectinload(ChatModel.users),
                    selectinload(ChatModel.bots)
                ).filter(ChatModel.id == chat_id)
                result = await session.execute(chat_query)
                db_chat = result.scalar_one_or_none()
                if not db_chat:
                    raise ValueError(f"聊天 {chat_id} 不存在")

                user_query = select(UserModel).filter(UserModel.id == user_id)
                result = await session.execute(user_query)
                db_user = result.scalar_one_or_none()
                if not db_user:
                    raise ValueError(f"用户 {user_id} 不存在")

                if db_user in db_chat.users:
                    db_chat.users.remove(db_user)

            await session.refresh(db_chat)
            return await self.chat_to_schema(db_chat)

    async def get_all_chats(self):
        async with self.db as session:
            result = await session.execute(select(ChatModel).options(
                selectinload(ChatModel.users),
                selectinload(ChatModel.bots),
                selectinload(ChatModel.current_haiguitang)
            ))
            db_chats = result.scalars().all()
            return [await self.chat_to_schema(chat) for chat in db_chats]

    async def get_chat_messages(self, chat_id: str) -> List[Message]:
        async with self.db as session:  # 使用 self.db 而不是 self.db.begin()
            result = await session.execute(
                select(MessageModel).where(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at)
            )
            messages = result.scalars().all()
            return [Message.from_orm(msg) for msg in messages]