from typing import List
from app.models.schemas import Message
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import os

class AnthropicService:
    def __init__(self):
        # 初始化 Anthropic 客户端
        # 注意: 你需要设置 ANTHROPIC_API_KEY 环境变量
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def generate_response(self, chat_messages: List[Message], chat_id: str, bot_id: str, model: str) -> str:
        # 将 Message 对象转换为 Anthropic 期望的格式
        prompt = ""
        for msg in chat_messages:
            if msg.role == "user":
                prompt += f"{HUMAN_PROMPT} {msg.content}"
            else:
                prompt += f"{AI_PROMPT} {msg.content}"

        try:
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens_to_sample=1000
            )
            return response.completion
        except Exception as e:
            print(f"Anthropic API 调用出错: {str(e)}")
            return "抱歉,生成响应时出现了错误。"