from langchain.tools import tool
from pydantic import BaseModel, Field


@tool
class ConductResearchSchema(BaseModel):
    """
    세부 연구 조사를 하위 전문 연구 조사 에이전트(Sub-agent)에게 위임하는 도구  

    이 도구는 상위 Supervisor 에이전트가 복잡한 연구 과제를 세분화하고,  
    각 주제별로 전문 연구 조사 에이전트에게 분배할 때 사용한다.  
    연구 주제는 반드시 하나의 구체적인 조사 단위(한 문단 이상의 설명 포함)로 정의되어야 하며,  
    명확한 범위와 조사 초점을 포함해야 한다.

    Tool for delegating a specific research investigation to a specialized sub-agent.

    This tool allows the supervisor agent to break down a complex investigation task  
    into smaller, well-defined topics that can be delegated to individual  
    research sub-agents. The topic must be a single, detailed investigation unit  
    (at least a paragraph of explanation) describing what needs to be examined.
    
    Attributes:
        research_topic (str):  
            조사할 구체적 연구 주제. 단일 주제여야 하며,  
            명확한 범위와 세부 설명(한 문단 이상)을 포함해야 한다.  
            The topic to investigate. Should represent a single, clearly defined topic,  
            described in high detail (at least a paragraph).
    """

    # 조사할 세부 연구 주제
    # specific research topic to be investigated by a sub-agent
    research_topic: str = Field(
        ...,
        description=(
            'The topic to investigate. Should be a single topic, and '
            'should be described in high detail (at least a paragraph).'
        )
        # description='조사할 연구 주제. 단일하고 명확한 주제여야 하며, 적어도 한 문단 이상의 구체적인 설명을 포함해야 한다.'
    )


@tool
class ResearchCompleteSchema(BaseModel):
    """
    연구 조사 프로세스가 완료되었음을 Supervisor 에이전트에 알리는 도구  

    이 도구는 하위 연구 조사 에이전트가 자신의 조사 단계를 모두 마치고,  
    Supervisor 에이전트에게 결과를 전달할 준비가 되었음을 나타낼 때 사용한다.  
    Supervisor는 이 신호를 기반으로 다음 단계(결과 종합 또는 보고서 작성)를 진행한다.

    Tool for signaling that the research investigation process is complete.

    This tool is used by a research sub-agent to notify the supervisor agent  
    that the investigation task is complete and ready for review or synthesis.  
    The supervisor can then proceed to aggregate findings or generate the final report.
    """
    # 추가 속성 없음 — 완료 신호만 전달
    # No additional fields — serves as a simple completion signal
    pass