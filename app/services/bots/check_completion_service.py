from typing import List
from app.models.orm import MessageModel
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings  # 导入配置

class StoryCompletionChecker:
    def __init__(self):
        # 初始化 ChatOpenAI 实例，使用配置中的 API 密钥
        self.chat = ChatOpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY)

    async def check_story_completion(self, story: str, messages: List[MessageModel]) -> bool:
        system_message = SystemMessage(content="你是一个海龟汤游戏的裁判，负责判断玩家是否已经还原了完整的故事细节。")

        # 将消息列表转换为字符串
        messages_str = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])

        human_message_content = f"""
            原始故事：
            {story}

            对话记录：
            {messages_str}

            请分析上述对话记录，判断是否已经还原了原始故事的完整细节。
            如果已经还原了���整细节，请只回答"是"；如果还没有完全还原，请只回答"否"。
            """

        human_message = HumanMessage(content=human_message_content)

        messages = [system_message, human_message]

        response = await self.chat.ainvoke(messages)
        print("==============response==============", response.content)
        return response.content.strip().lower() == "是"

    # 这里可以添加未来的其他方法
    # 例如：
    # async def some_other_method(self):
    #     pass



    ### 下一步完整的实现，游戏结束，游戏提示，输入的提问合规校验