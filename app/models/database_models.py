from app.models.chat import Base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

class BotDB(Base):
    # ... 其他字段 ...
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())