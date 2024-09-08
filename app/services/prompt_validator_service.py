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
    "多少", "哪个", "几", "怎么回事", "怎么样", "为啥", "如何回事", "怎么不", "能否", 
    "是否", "可否", "有无", "怎样", "哪些", "为哪般", "啥", "啥子", "哪一", 
    "多长时间", "怎样才", "哪个地方", "哪种", "哪怕", "怎样的", "哪一位", "为何", 
    "哪里能", "何时", "何地", "多少个",
    "为何", "哪些", "怎么做", "什么原因", "什么情况", "怎样的情况", "什么问题", 
    "谁来", "什么时间"
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