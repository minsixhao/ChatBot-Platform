from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.models.enums import MessageRole, ModelType, ServiceProvider, SenderType
from app.config import settings
from typing import List, Dict, Any
from app.models.chat import Message
from app.repositories.message_repository import get_chat_messages
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_client = ChatOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = ChatAnthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            model_name="claude-3-5-sonnet-20240620"
        )

    async def generate_response(self, message: str, chat_id: str, bot_id: str, model_type: ModelType) -> str:
        provider, model = self._get_provider_and_model(model_type)
        
        if provider == ServiceProvider.OPENAI:
            return await self._generate_openai_response(message, chat_id, bot_id, model)
        elif provider == ServiceProvider.ANTHROPIC:
            return await self._generate_anthropic_response(message, chat_id, bot_id, model)
        else:
            raise ValueError(f"不支持的服务提供商: {provider}")

    def _get_provider_and_model(self, model_type: ModelType) -> tuple[ServiceProvider, str]:
        model_mapping = {
            ModelType.GPT3: (ServiceProvider.OPENAI, "gpt-3.5-turbo"),
            ModelType.GPT4O: (ServiceProvider.OPENAI, "gpt-4o"),
            ModelType.CLAUDE: (ServiceProvider.ANTHROPIC, "claude-3-5-sonnet-20240620"),
        }
        return model_mapping.get(model_type, (None, None))

    async def _generate_openai_response(self, content: str, chat_id: str, bot_id: str, model: str, **kwargs) -> str:
        # 获取聊天历史记录
        print("===========chat_id============", chat_id)
        chat_history = await self._get_chat_history(chat_id)
        print("===========chat_history============", chat_history)
        # 格式化聊天历史记录
        formatted_history = self._format_chat_history(chat_history)
        print("===========formatted_history============", formatted_history)
        # 添加当前消息
        formatted_history.append(HumanMessage(content=content))
        print("===========formatted_history============", formatted_history)
        # 调用具体生成内容的方法
        return await self._generate_openai_content(formatted_history, model, **kwargs)

    async def _get_chat_history(self, chat_id: str) -> List[Dict[str, str]]:
        logger.info(f"获取聊天历史记录，chat_id: {chat_id}")
        messages = await get_chat_messages(chat_id)
        
        chat_history = []
        for message in messages:
            chat_history.append({
                "role": "user" if message.sender_type == SenderType.USER else "assistant",
                "content": message.content
            })

        logger.info(f"成功获取到 {len(chat_history)} 条聊天记录")
        return chat_history

    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> List[HumanMessage | SystemMessage]:
        # 将聊天历史记录转换为LangChain可以接受的消息格式
        formatted_messages = []
        for msg in chat_history:
            if msg['role'] == 'user':
                formatted_messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                formatted_messages.append(AIMessage(content=msg['content']))
        return formatted_messages

    async def _generate_openai_content(self, messages: List[HumanMessage | SystemMessage], model: str, **kwargs) -> str:
        chat = self.openai_client.with_config(model=model)
        
        # 设置额外的参数，如stream和temperature
        extra_params = {
            "stream": kwargs.get("stream", False),
            "temperature": kwargs.get("temperature", 0.7),
            # 可以添加其他参数
        }
        
        response = await chat.ainvoke(messages, **extra_params)
        return response.content.strip()

    async def _generate_anthropic_response(self, message: str, chat_id: str, model: str) -> str:
        # 获取聊天历史记录
        chat_history = await self._get_chat_history(chat_id)
        
        # 格式化聊天历史记录
        formatted_history = self._format_chat_history(chat_history)
        
        # 添加当前消息
        formatted_history.append(HumanMessage(content=message))
        
        chat = self.anthropic_client.with_config(model_name=model)
        response = await chat.ainvoke(formatted_history)
        return response.content.strip()