from pydantic import BaseModel, Field

class UserIntentClarificationSchema(BaseModel):
    """
    사용자의 의도 명확화(clarification)하는 결정과 질문을 정의하는 Pydantic 데이터 스키마
    Schema for user clarification decision and questions.

    Attributes:
        need_clarification (bool): 
            사용자가 명확화 질문을 받아야 하는지 여부를 나타내는 필드
        question (str): 
            리포트 범위를 명확히 하기 위해 사용자에게 던지는 질문을 담는 필드
        verification (str): 
            사용자가 필요한 정보를 제공한 후 연구를 시작할 것임을 알리는 메시지를 담는 필드
    """
    need_clarification: bool = Field(
        ...,
        #description='사용자가 명확화 질문을 받아야 하는지 여부를 나타내는 필드'
        description='Whether the user needs to be asked a clarifying question.'
    )
    question: str = Field(
        ...,
        #description='리포트 범위를 명확히 하기 위해 사용자에게 던지는 질문을 담는 필드'
        description='A question to ask the user to clarify the report scope'
    )
    verification: str = Field(
        ...,
        #description='사용자가 필요한 정보를 제공한 후 연구를 시작할 것임을 알리는 메시지를 담는 필드'
        description='Verify message that we will start research after the user has provided the necessary information.'
    )


class ResearchQuestionSchema(BaseModel):
    """
    구조화한 연구 개요(brief)를 정의하는 Pydantic 데이터 스키마
    Schema for structured research brief generation.

    Attributes:
        research_brief (str): 
            연구를 안내하기 위해 사용되는 연구 질문을 담는 필드
    """
    research_brief: str = Field(
        ...,
        #description='연구를 수행하는 데 지침으로 활용할 연구 질문을 담는 필드'
        description='A research question that will be used to guide the research.'
    )