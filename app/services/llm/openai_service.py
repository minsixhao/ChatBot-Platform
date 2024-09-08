from typing import List
from app.models.enums import MessageRole
from app.models.schemas import Message
from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class PromptValidation(BaseModel):
    is_valid: bool = Field(description="提示是否是有效的海龟汤提问")
    reason: str = Field(description="判断的理由")

class OpenAIService:
    def __init__(self):
        self.chat_model = ChatOpenAI(
            model='gpt-4o', 
            openai_api_key=settings.OPENAI_API_KEY, 
            # openai_api_base='https://api.deepseek.com',
            # max_tokens=1024
        )
        self.validation_model = ChatOpenAI(
            model='gpt-3.5-turbo-0613',
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0
        )

    async def generate_response(self, chat_messages: List[Message], chat_id: str, bot_id: str, model: str) -> str:
        # 定义汤面和汤底
        tang_mian = "女主很喜欢在网上分享自己的近况，有一天她收到一则留言，被吓到的女主夺门而出。或许她不该逃，第二天警方发现了女孩的尸体。"
        tang_di = "女主在网上分享自己的近况的同时泄露了很多个人信息，其中包括她的家庭住址。有一天，一个变态通过女主的博文推断出了女主的家庭住址，藏匿到了女主的家里。女主在家时，他给女主发了一句：”我正在看着你。“女主被吓得夺门而出，变态从家里追了出来，在争执之中，变态失手把女主给杀了。"
        
        # 定义示例

        examples = [
            {"input": "是亲哥哥吗？", "output": "是的。"},
            {"input": "大哥也生病了吗？", "output": "无关，大哥身体一直很健康。"},
            {"input": "你们家里几个人？", "output": "无关，家里有三个兄弟。"},
            {"input": "大哥是想杀我吗？", "output": "不是。"}
        ]

        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )

        # 创建系统提示模板
        system_template = """我正在进行一个海龟汤游戏，这是一个情境猜谜游戏。我会根据谜题情境（汤面）进行推理，并通过提问来猜出真相（汤底）。我的任务是回答你的提问。游戏规则如下：

                你的提问内容应参考谜题情境（汤面），汤面会在下方提供。

                你可以提出任何问题，我会根据真相（汤底）帮助你推理，我只会回答你“是的”、“不是”或“无关”。

                回答“是的”、“不是”和“无关”的情况如下：

                1. 是的：当玩家的问题直接指向谜题的某个关键点，并且该点与谜题的答案相关且正确时，回答“是的”。

                2. 不是：当玩家的问题直接指向谜题的某个关键点，但该点与谜题的答案不相关或不正确时，回答“不是”。

                3. 无关：当玩家的问题与谜题的核心内容无关，或者问题本身没有明确的指向性，无法帮助玩家缩小答案范围时，回答“无关”。

                例如，假设谜题是“一个人在房间里，房间里有一扇门和一扇窗户，这个人是怎么出去的？”

                - 玩家问：“这个人是通过门出去的吗？” 如果答案是通过门出去的，回答“是的”；如果不是，回答“不是”。

                - 玩家问：“这个人是通过窗户出去的吗？” 如果答案是通过窗户出去的，回答“是的”；如果不是，回答“不是”。

                - 玩家问：“这个人是通过烟囱出去的吗？” 如果房间里没有烟囱，或者这个问题与谜题无关，回答“无关，（这里补充简短的提示）”。


                如果用户的问题与汤底有关，我会回答“无关”。

                我会参考其他对话消息的格式，回答你的提问。

                汤面：{tang_mian}
                汤底：{tang_di}

                开始吧！请你提问！
            """

        # 创建最终的提示模板
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            few_shot_prompt,
            ("human", "{input}"),
        ])

        print("============final_prompt============:", final_prompt)

        # 创建链
        chain = final_prompt | self.chat_model

        # 准备输入
        input_message = next((msg.content for msg in reversed(chat_messages) if msg.role == MessageRole.USER), "")

        try:
            response = await chain.ainvoke({
                "tang_mian": tang_mian,
                "tang_di": tang_di,
                "input": input_message
            })
            return response.content
        except Exception as e:
            print(f"OpenAI API 调用出错: {str(e)}")
            return "抱歉，生成响应时出现了错误。"


    