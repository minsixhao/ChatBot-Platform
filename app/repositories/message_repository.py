from sqlalchemy import select
from app.models.chat import MessageModel  # 注意这里改为 MessageModel
from app.db.database import execute_query

async def get_chat_messages(chat_id: str):
    query = select(MessageModel).where(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at)
    return await execute_query(query)