import operator
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from typing import Annotated, Sequence


class AgentInputState(MessagesState):
    """
    전체 에이전트의 입력 상태를 정의하는 그래프 상태 클래스

    사용자 입력 메시지만 포함한다.

    Input state for the full agent - only contains messages from user input.

    Attributes:
        messages (list[BaseMessage]): 사용자 입력 메시지 목록
    """
    pass


class AgentState(MessagesState):
    """
    전체 멀티-에이전트 리서치 시스템의 주요 그래프 상태 클래스  

    MessagesState를 확장하여 리서치 조율을 위한 추가 필드를 포함한다.  
    참고: 일부 필드는 서브그래프와 메인 워크플로우 간의 상태 관리를 위해 
    여러 그래프 상태 클래스에서 중복 정의한다.
    
    Main state for the full multi-agent research system.
    
    Extends MessagesState with additional fields for research coordination.
    Note: Some fields are duplicated across different state classes for proper
    state management between subgraphs and the main workflow.
    
    Attributes:
        research_brief (str | None):  
            사용자 대화 히스토리에서 생성된 리서치 요약문  
            (없을 수도 있으므로 `None` 허용)

        supervisor_messages (Sequence[BaseMessage]):  
            리서치 조율을 위해 supervisor agent와 교환된 메시지

        raw_notes (list[str]):  
            리서치 단계에서 수집한 가공되지 않은 원시 연구 노트

        notes (list[str]):  
            보고서 생성을 위해 정리 및 구조화한 연구 노트

        final_report (str):  
            최종적으로 생성한 포맷팅된 연구 보고서
    """
    
    research_brief: str | None                                           # research brief generated from user conversation history
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages]  # messages exchanged with the supervisor agent for coordination
    raw_notes: Annotated[list[str], operator.add] = []                   # raw unprocessed research notes collected during the research phase
    notes: Annotated[list[str], operator.add] = []                       # processed and structured notes ready for report generation
    final_report: str                                                    # final formatted research report