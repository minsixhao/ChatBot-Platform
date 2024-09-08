from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.orm import GroupChatModel, UserModel, BotModel
from app.models.schemas import GroupChatCreate, GroupChat
from typing import List

class GroupChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_group_chat(self, group_chat: GroupChatCreate) -> GroupChat:
        db_group_chat = GroupChatModel(
            name=group_chat.name,
            creator_id=group_chat.creator_id
        )
        users = await self.db.execute(select(UserModel).where(UserModel.id.in_(group_chat.user_ids)))
        bots = await self.db.execute(select(BotModel).where(BotModel.id.in_(group_chat.bot_ids)))
        
        db_group_chat.users = users.scalars().all()
        db_group_chat.bots = bots.scalars().all()

        self.db.add(db_group_chat)
        await self.db.commit()
        await self.db.refresh(db_group_chat)
        return GroupChat.from_orm(db_group_chat)

    # 添加其他方法，如获取群聊、添加/删除成员等