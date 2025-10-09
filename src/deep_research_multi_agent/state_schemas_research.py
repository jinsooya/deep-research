import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence, TypedDict


class ResearcherState(TypedDict):
    """
    리서치 에이전트의 상태(대화 히스토리, 리서치 메타데이터 등)를 정의하는 그래프 상태 클래스  
    State for the research agent containing message history and research metadata
    
    이 상태는 리서처의 대화 히스토리, 도구 호출 제한을 위한 반복 횟수,  조사 중인 연구 주제, 
    압축된 연구 결과, 그리고 세부 분석을 위한 원시 연구 노트를 추적한다.  
    This state tracks the researcher's conversation, iteration count for limiting  
    tool calls, the research topic being investigated, compressed findings,  
    and raw research notes for detailed analysis.

    Attributes:
        researcher_messages (Sequence[BaseMessage]):  
            리서처 에이전트의 대화 히스토리를 저장하는 메시지 시퀀스  
            Message history of the researcher agent  

        tool_call_iterations (int):  
            툴 호출 횟수를 추적하여 반복 실행을 제한하기 위한 카운터  
            Iteration count for limiting tool calls  

        research_topic (str): 현재 조사 중인 연구 주제  
            The specific research topic being investigated  

        compressed_research (str): 
            중간 요약 또는 압축된 연구 결과를 저장하는 필드  
            Compressed summary of accumulated research findings  

        raw_notes (list[str]): 리서치 과정에서 수집된 원시 연구 노트 목록  
            Raw research notes collected during the research process
    """
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]  # message history of the research agent
    tool_call_iterations: int                                            # counter for tool call iterations
    research_topic: str                                                  # current research topic being investigated
    compressed_research: str                                             # compressed or summarized research findings
    raw_notes: Annotated[list[str], operator.add]                        # collected raw research notes


class ResearcherOutputState(TypedDict):
    """
    리서치 에이전트의 최종 출력을 정의하는 그래프 상태 클래스  
    Output state for the research agent containing final research results
    
    이 상태는 연구 프로세스의 최종 결과를 나타내며, 압축된 연구 결과와 
    전체 원시 연구 노트를 포함한다.  
    This represents the final output of the research process with compressed  
    research findings and all raw notes from the research process.

    Attributes:
        compressed_research (str): 최종 압축된 연구 결과  
            Final compressed research findings  

        raw_notes (list[str]): 전체 리서치 과정에서 수집된 원시 연구 노트  
            All raw research notes from the research process  

        researcher_messages (Sequence[BaseMessage]):  
            리서처의 최종 대화 메시지 기록  
            Final message history of the researcher agent
    """
    ccompressed_research: str                                            # final compressed research output
    raw_notes: Annotated[list[str], operator.add]                        # all collected raw research notes
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]  # final researcher message history