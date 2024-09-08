from app.models.enums import ModelType, ServiceProvider
from app.repositories.bot_repository import BotRepository
from app.models.schemas import BotCreate, Bot, Message
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from app.services.llm.openai_service import OpenAIService
from app.services.llm.anthropic_service import AnthropicService
from app.services.bots.check_completion_service import StoryCompletionChecker

class BotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BotRepository(db)
        self.openai_service = OpenAIService()
        self.anthropic_service = AnthropicService()
        self.story_completion_checker = StoryCompletionChecker()

    async def create_bot(self, bot: BotCreate) -> Bot:
        return await self.repository.create_bot(bot)

    async def get_bot(self, bot_id: str) -> Optional[Bot]:
        return await self.repository.get_bot(bot_id)
    
    async def update_bot(self, bot_id: str, bot_data: dict) -> Optional[Bot]:
        return await self.repository.update_bot(bot_id, bot_data)
    
    async def delete_bot(self, bot_id: str) -> bool:
        return await self.repository.delete_bot(bot_id)
    
    async def generate_chat_message_response(self, chat_messages: List[Message], chat_id: str, bot_id: str) -> str:

        model_type: ModelType = ModelType.GPT4O
        provider, model = self.get_provider_and_model(model_type)
        
        if provider == ServiceProvider.OPENAI:
            return await self.generate_openai_response(chat_messages, chat_id, bot_id, model)
        elif provider == ServiceProvider.ANTHROPIC:
            return await self.generate_anthropic_response(chat_messages, chat_id, bot_id, model)
        else:
            raise ValueError(f"不支持的服务提供商: {provider}")

    async def generate_openai_response(self, chat_messages: List[Message], chat_id: str, bot_id: str, model: str) -> str:
        # 实现 OpenAI 响应生成逻辑
        return await self.openai_service.generate_response(chat_messages, chat_id, bot_id, model)

    async def generate_anthropic_response(self, chat_messages: List[Message], chat_id: str, bot_id: str, model: str) -> str:
        # 实现 Anthropic 响应生成逻辑
        return await self.anthropic_service.generate_response(chat_messages, chat_id, bot_id, model)
    
    def get_provider_and_model(self, model_type: ModelType) -> Tuple[ServiceProvider, str]:
        model_mapping = {
            ModelType.GPT3: (ServiceProvider.OPENAI, "gpt-3.5-turbo"),
            ModelType.GPT4: (ServiceProvider.OPENAI, "gpt-4"),  # 添加这行
            ModelType.GPT4O: (ServiceProvider.OPENAI, "gpt-4"),
            ModelType.CLAUDE: (ServiceProvider.ANTHROPIC, "claude-v1"),
            ModelType.LLM: (ServiceProvider.OPENAI, "text-davinci-003"),
        }
        # 使用get方法，如果没有找到对应的模型类型，则返回GPT3的配置
        return model_mapping.get(model_type, (ServiceProvider.OPENAI, "gpt-3.5-turbo"))

    async def check_story_completion(self, story: str, messages: List[Message]) -> bool:
        return await self.story_completion_checker.check_story_completion(story, messages)

    async def handle_story_completion(self, chat_id: str, story: str, messages: List[Message]) -> List[Message]:
        is_completed = await self.check_story_completion(story, messages)
        
        if is_completed:
            completion_message = Message(
                chat_id=chat_id,
                content="恭喜！你已经成功还原了完整的故事细节。",
                role="system",
                sender_id="system",
                sender_type="SYSTEM"
            )
            # 这里假设你有一个方法来添加消息
            # 你可能需要在 ChatRepository 中添加这个方法
            return await self.chat_repository.add_message(chat_id, completion_message)
        
        return messages