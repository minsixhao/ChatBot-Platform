from enum import Enum

class ModelType(Enum):
    GPT3 = "gpt3"
    GPT4O = "gpt-4o"
    CLAUDE = "claude"
    LLM = "llm"  # 添加这一行

class ServiceProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class SenderType(Enum):
    USER = "user"
    BOT = "bot"

class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"