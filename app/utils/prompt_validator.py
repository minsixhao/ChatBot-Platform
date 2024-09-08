from app.core.config import settings
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class PromptValidation(BaseModel):
    is_valid: bool = Field(description="提示是否是有效的海龟汤提问")
    reason: str = Field(description="判断的理由")

validation_model = ChatOpenAI(
    model='gpt-4',
    openai_api_key=settings.OPENAI_API_KEY,
)

keywords = [
    "为什么", "怎么", "什么", "谁", "哪里", "哪儿", "什么时候", "如何", 
    # ... 其他关键词 ...
    "死者生前最后见到的人是谁？",
    "案发现场有什么特别的地方吗？"
]

async def validate_prompt(prompt: str) -> PromptValidation:
    is_valid = True
    reason = "提示是有效的海龟汤提问。"

    for keyword in keywords:
        if keyword in prompt:
            is_valid = False
            reason = f"提示包含无效关键词：'{keyword}'。海龟汤提问应该是陈述句，不应包含疑问词。"
            break

    return PromptValidation(is_valid=is_valid, reason=reason)

# 测试函数可以保留在原文件中或移动到测试目录