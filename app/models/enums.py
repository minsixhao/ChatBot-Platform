from enum import Enum

class ModelType(Enum):
    GPT3 = "gpt3"
    GPT4 = "gpt4"  # 添加这行
    GPT4O = "gpt-4o"
    CLAUDE = "claude"
    LLM = "llm"

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

class ChatType(Enum):
    SINGLE = "SINGLE"
    GROUP = "GROUP"