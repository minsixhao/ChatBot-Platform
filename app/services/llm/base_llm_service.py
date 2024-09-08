from abc import ABC, abstractmethod
from typing import List
from app.models.schemas import Message

class BaseLLMService(ABC):
    @abstractmethod
    async def generate_response(self, chat_messages: List[Message], chat_id: str, bot_id: str, model: str) -> str:
        pass