import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence, TypedDict


class ResearcherState(TypedDict):
    """
    연구 조사 에이전트(대화 히스토리, 리서치 메타데이터 등) 그래프 상태를 정의하는 클래스  
    
    이 상태는 연구 조사 에이전트의 대화 히스토리, 도구 호출 제한을 위한 반복 횟수, 조사 중인 연구 주제, 
    압축된 연구 결과, 그리고 세부 분석을 위한 원시 연구 노트를 추적한다.  
    
    State for the research agent containing message history and research metadata

    This state tracks the researcher's conversation, iteration count for limiting  
    tool calls, the research topic being investigated, condensed findings,  
    and raw research notes for detailed analysis.

    Attributes:
        researcher_messages (Sequence[BaseMessage]):  
            연구 조사 에이전트의 대화 히스토리를 저장하는 메시지 시퀀스  
            Message history of the researcher agent  
        tool_call_iterations (int):  
            도구 호출 횟수를 추적하여 반복 실행을 제한하기 위한 카운터  
            Iteration count for limiting tool calls  
        research_topic (str): 현재 조사 중인 연구 주제  
            The specific research topic being investigated  
        condensed_research (str): 
            중간 요약 또는 압축된 연구 조사 결과를 저장하는 필드  
            Condensed summary of accumulated research findings  
        raw_notes (list[str]): 연구 조사 과정에서 수집한 원시 연구 노트 목록  
            Raw research notes collected during the research process
    """
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]  # message history of the research agent
    tool_call_iterations: int                                            # counter for tool call iterations
    research_topic: str                                                  # current research topic being investigated
    condensed_research: str                                              # condensed or summarized research findings
    raw_notes: Annotated[list[str], operator.add]                        # collected raw research notes


class ResearcherOutputState(TypedDict):
    """
    연구 조사 에이전트의 최종 출력을 정의하는 그래프 상태 클래스  
    
    이 상태는 연구 조사 프로세스의 최종 결과를 나타내며, 
    압축한 연구 결과와 전체 원시 연구 노트를 포함한다.  

    Output state for the research agent containing final research results

    This represents the final output of the research process with condensed  
    research findings and all raw notes from the research process.

    Attributes:
        condensed_research (str): 최종 압축한 연구 조사 결과  
            Final condensed research findings  
        raw_notes (list[str]): 전체 연구 조사 과정에서 수집한 원시 연구 노트  
            All raw research notes from the research process  
        researcher_messages (Sequence[BaseMessage]):  
            연구 조사 에이전트의 최종 대화 메시지 기록  
            Final message history of the researcher agent
    """
    condensed_research: str                                              # final condensed research output
    raw_notes: Annotated[list[str], operator.add]                        # all collected raw research notes
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]  # final researcher message history


class SupervisorState(TypedDict):
    """
    멀티 에이전트 연구 감독(Supervisor)의 그래프 상태를 정의하는 클래스  
       
    이 상태는 여러 연구 조사 하위 에이전트(research sub-agents) 간의 
    조정을 담당하는 상위 감독 에이전트의 상태를 관리한다. 
    연구 조사 진행 상황, 하위 에이전트의 중간 결과, 누적된 연구 노트,  
    그리고 최종 보고서 작성을 위한 구조화된 노트를 추적한다.
    
    State for the multi-agent research supervisor.
    
    This state manages coordination between the supervisor and multiple  
    research sub-agents. It tracks progress, collects intermediate findings,  
    and maintains structured notes for final report synthesis.
    
    Attributes:
        supervisor_messages (Sequence[BaseMessage]):  
            감독 에이전트와의 대화 및 의사결정 로그를 저장하는 메시지 시퀀스  
            Message history exchanged between supervisor and sub-agents  
            for coordination and decision-making.
        research_brief (str):  
            연구 조사의 전체 방향을 정의하는 핵심 브리프(연구 주제, 범위, 목표 등)  
            The detailed research brief guiding overall research direction.
        notes (list[str]):  
            정리한 노트 — 중간 결과를 구조화해 최종 보고서에 바로 활용 가능한 형태로 저장  
            Processed and structured notes ready for final report generation.
        research_iterations (int):  
            연구 조사 루프의 반복 횟수를 추적하여 연구 조사 진행 단계를 관리  
            Counter tracking the number of research iterations performed.
        raw_notes (list[str]):  
            하위 연구 조사 에이전트들로부터 수집한 원시 연구 노트  
            Raw, unprocessed research notes collected from sub-agent findings.
    """
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages]  # messages exchanged with supervisor for coordination and decision-making
    research_brief: str                                 # detailed research brief that guides the overall research direction
    notes: Annotated[list[str], operator.add] = []      # processed and structured notes ready for final report generation
    research_iterations: int = 0                        # counter tracking the number of research iterations performed
    raw_notes: Annotated[list[str], operator.add] = []  # raw unprocessed research notes collected from sub-agent research