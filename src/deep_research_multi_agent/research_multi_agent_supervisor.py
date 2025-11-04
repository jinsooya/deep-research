###############################################################################
### Deep Research Multi-Agent: 연구 조사 다중 에이전트 감독 모듈 ######################
###############################################################################
# --- 모듈 임포트 ----------------------------------------------------------------
# 이 모듈은 감독 에이전트 (Supervisor Agent) 패턴을 구현한다:
# 1) 감독 에이전트가 연구 조사를 조정하고 하위 에이전트에게 과제를 위임한다.
# 2) 여러 연구 조사 에이전트가 각기 다른 하위 주제를 독립적으로 수행한다.
# 3) 하위 결과를 집계/압축하여 최종 보고에 활용한다.
# 감독 에이전트는 병렬 실행으로 효율을 높이되, 주제별로 컨텍스트를 분리해 관리한다.
#
# Multi-agent supervisor for coordinating research across multiple specialized agents.
# This module implements a supervisor pattern where:
# 1) A supervisor agent coordinates research activities and delegates tasks
# 2) Multiple researcher agents work on specific sub-topics independently
# 3) Results are aggregated and compressed for final reporting
# The supervisor uses parallel research execution to improve efficiency while
# maintaining isolated context windows for each research topic.
# -----------------------------------------------------------------------------

import asyncio
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_core.runnables import Runnable, RunnableConfig
from langchain.messages import SystemMessage, ToolMessage, HumanMessage
from langchain.chat_models import init_chat_model


from deep_research_multi_agent.state_schemas_research import SupervisorState
from deep_research_multi_agent.research_agent import researcher_workflow
from deep_research_multi_agent.tools import get_tools#, reflection_tool
from deep_research_multi_agent.utils import get_today_str, get_notes_from_tool_calls

from deep_research_multi_agent.prompts import RESEARCH_SUPERVISOR_INSTRUCTION

# --- 노드 클래스 ----------------------------------------------------------------
class SupervisorAgentNode:
    """
    연구 조사 감독 에이전트 노드 클래스  

    LangGraph 기반 다중 연구 조사 시스템에서 '상위 감독자(Supervisor)' 역할을 
    수행하는 노드 클래스다.  
    이 노드는 전체 연구 브리프를 분석하고, 각 하위 에이전트에게 세부 연구 조사를 위임하거나  
    연구 완료 여부를 결정하는 역할을 한다.

    주요 기능:
    - 연구 지시 단계: 어떤 주제들을 조사할지 판단하고, ConductResearchSchema 도구를 호출하도록 유도
    - 연구 진행 제어: 각 연구 조사 주제의 반복 한도나 병렬 실행 수를 관리
    - 연구 종료 판단: 모든 주제가 완료되었는지, 종료 조건에 도달했는지를 결정

    Key Responsibilities:
    1. Analyze the research brief and current progress.
    2. Decide what topics to investigate next.
    3. Coordinate sub-agent activities.
    4. Determine when the research process should conclude.
    """
    def __init__(self, runnable: Runnable) -> None:
        """
        SupervisorAgentNode의 초기화 메소드
        
        Args:
            runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)            
        """
        self.runnable: Runnable = runnable  # supervisor_model_with_tools
    
    async def __call__(self, state: SupervisorState, config: RunnableConfig | None = None) -> Command[Literal['Supervisor Tools']]:
    # async def __call__(self, state: MessagesState, config: RunnableConfig | None = None) -> MessagesState:
        """
        이 메서드는 LangGraph에서 실행될 때 SupervisorState를 입력으로 받아,  
        현재의 연구 진행 상황(메시지 히스토리, 반복 횟수 등)을 분석한 뒤  
        '다음에 어떤 도구(supervisor_tools)를 실행할지' 결정한다.

        내부 수행 단계:
        1) 현재 Supervisor 메시지 이력(supervisor_messages) 로드  
        2) 오늘 날짜와 실행 제한 정보를 포함한 시스템 프롬프트 생성  
        3) Supervisor 모델(self.runnable)에 메시지를 전달하여 LLM 의사결정 수행  
        4) 새로운 Supervisor 메시지를 상태에 업데이트하고 다음 노드(supervisor_tools)로 이동
        
        Coordinate research activities.
        
        Analyzes the research brief and current progress to decide:
        - What research topics need investigation
        - Whether to conduct parallel research
        - When research is complete
        
        Args:
            state (SupervisorState): 이전 상호작용을 포함한 현재 그래프 상태
                Current supervisor state with messages and research progress
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            Command[Literal['Supervisor Tools']]:  
                다음 노드(supervisor_tools)로 이동하도록 지시하는 LangGraph Command 객체
                Command to proceed to supervisor_tools node with updated state
        """
        supervisor_messages = state.get('supervisor_messages', [])

        # 오늘 날짜/제약 포함한 시스템 메시지 구성
        # prepare system message with current date and constraints
        instruction = RESEARCH_SUPERVISOR_INSTRUCTION.format(
            date=get_today_str(), 
            max_concurrent_research_units=MAX_CONCURRENT_RESEARCHERS,
            max_researcher_iterations=MAX_RESEARCHER_ITERATIONS
        )
        messages = (
            [SystemMessage(content=instruction)] 
            + supervisor_messages
        )

        # 다음 단계 의사결정(도구 호출 포함 가능)
        # make decision about next research steps
        # response = await supervisor_model_with_tools.ainvoke(messages)
        response = await self.runnable.ainvoke(messages)
        
        return Command(
            goto='Supervisor Tools',
            update={
                'supervisor_messages': [response],
                'research_iterations': state.get('research_iterations', 0) + 1
            }
        )

# --- 노드 함수 -----------------------------------------------------------------
# NOTE: LLM을 사용하지 않으면 클래스 대신 함수로 정의해서 '클래스'와 '함수’로 이 둘의 차이를 구분한다. 
async def supervisor_tools_node(state: SupervisorState, config: RunnableConfig | None = None) -> Command[Literal['Supervisor Agent', '__end__']]:
# async def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
    """
    연구 조사 감독 에이전트 노드 함수  

    이 노드는 SupervisorAgentNode가 의사결정을 내린 후,
    해당 결정을 실제로 실행하는 역할을 담당한다.
    즉, 연구 조사 감독 에이전트가 이전 단계에서 의사결정을 내린 후 호출되며,
    연구 조사 감독 에이전트가 요청한 각 도구(`reflection_tool`, `ConductResearchSchema`) 
    등의 도구 호출을 실제 수행하고, 결과를 수집 및 가공하여 Supervisor 상태(State)에 반영한다.

    주요 기능:
    - 감독 에이전트의 도구 호출 실행 및 결과 수집
    - 병렬 연구 조사(parallel research) 실행
    - 연구 노트(raw_notes) 및 요약 결과(notes) 집계
    - 연구 종료 조건 판별 (연구 완료 시 END 노드로 이동)
    
    실행 흐름 요약:
    1) 현재 메시지 이력(supervisor_messages)과 반복 횟수 불러오기  
    2) 종료 조건 검사 (도구 호출 없음, 최대 반복 초과, 연구 완료 신호 등)  
    3) 남은 도구 호출이 있으면 실행 (reflection_tool -> 동기 / ConductResearchSchema -> 비동기 병렬)  
    4) 모든 실행 결과를 메시지로 변환하여 상태에 업데이트  
    5) 종료 조건에 따라 supervisor 또는 END 노드로 이동  
    
    Execute supervisor decisions - either conduct research or end the process.

    Handles:
    - Executing think_tool calls for strategic reflection
    - Launching parallel research agents for different topics
    - Aggregating research results
    - Determining when research is complete
    
    Args:
        state (SupervisorState): 이전 상호작용을 포함한 현재 그래프 상태
            Current supervisor state with messages and iteration count
        config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
            포함한 추가적인 설정을 할 수 있다.

    Returns:
        Command[Literal['Supervisor Agent', '__end__']]:  
            다음 실행할 노드(SupervisorAgentNode 또는 종료)를 지정한다.
            Command to continue supervision, end process, or handle errors
    """
    # 현재 상태에서 메시지 및 반복 횟수 불러오기
    supervisor_messages = state.get('supervisor_messages', [])
    research_iterations = state.get('research_iterations', 0)
    most_recent_message = supervisor_messages[-1]

    # 기본 반환값 초기화
    # initialize variables for single return pattern
    tool_messages = []
    all_raw_notes = []
    next_step = 'Supervisor Agent'  # default next step
    should_end = False

    # 종료 조건 검사
    # check exit criteria first
    exceeded_iterations = research_iterations >= MAX_RESEARCHER_ITERATIONS
    no_tool_calls = not most_recent_message.tool_calls
    research_complete = any(
        tool_call['name'] == 'ResearchCompleteSchema' 
        for tool_call in most_recent_message.tool_calls
    )

    if exceeded_iterations or no_tool_calls or research_complete:
        should_end = True
        next_step = END
    else:
        # 도구 실행 블록 (예외 처리 포함)
        # execute ALL tool calls before deciding next step
        try:
            # reflection_tool과 ConductResearchSchema 구분
            # separate reflection_tool calls from ConductResearchSchema calls
            reflection_tool_calls = [
                tool_call for tool_call in most_recent_message.tool_calls 
                if tool_call['name'] == 'reflection_tool'
            ]
            conduct_research_calls = [
                tool_call for tool_call in most_recent_message.tool_calls 
                if tool_call['name'] == 'ConductResearchSchema'
            ]
            # reflection_tool은 동기 실행
            # handle reflection_tool calls (synchronous)
            for tool_call in reflection_tool_calls:
                observation = get_tools(tool_names=['reflection_tool'])[0].invoke(tool_call['args'])
                # observation = reflection_tool.invoke(tool_call['args'])
                tool_messages.append(
                    ToolMessage(
                        content=observation,
                        name=tool_call['name'],
                        tool_call_id=tool_call['id']
                    )
                )
            # ConductResearchSchema는 비동기 병렬 실행
            # handle ConductResearchSchema calls (asynchronous)
            if conduct_research_calls:
                # 여러 하위 연구 조사 에이전트를 병렬로 실행
                # launch parallel research agents
                coros = [
                    researcher_workflow.ainvoke({
                        'researcher_messages': [
                            HumanMessage(content=tool_call['args']['research_topic'])
                        ],
                        'research_topic': tool_call['args']['research_topic']
                    }) 
                    for tool_call in conduct_research_calls
                ]
                # 병렬 실행 완료 대기
                # wait for all research to complete
                tool_results = await asyncio.gather(*coros)

                # 각 연구 결과를 ToolMessage로 변환
                # format research results as tool messages
                # each sub-agent returns compressed research findings in result['compressed_research']
                # we write this compressed research as the content of a ToolMessage, which allows
                # the supervisor to later retrieve these findings via get_notes_from_tool_calls()
                research_tool_messages = [
                    ToolMessage(
                        content=result.get('compressed_research', '연구 보고서를 종합(요약)하는 중 오류가 발생했습니다.'),  # 'Error synthesizing research report'
                        name=tool_call['name'],
                        tool_call_id=tool_call['id']
                    ) for result, tool_call in zip(tool_results, conduct_research_calls)
                ]
                
                tool_messages.extend(research_tool_messages)

                # 연구 노트(raw_notes) 병합
                # aggregate raw notes from all research
                all_raw_notes = [
                    '\n'.join(result.get('raw_notes', [])) 
                    for result in tool_results
                ]
        except Exception as err:
            print(f'감독 에이전트 도구(SupervisorToolsNode) 실행 중 오류가 발생했습니다: {err}')  # 'Error in Supervisor Tools'
            should_end = True
            next_step = END
    
    # 최종 상태 반환
    # single return point with appropriate state updates
    if should_end:
        return Command(
            goto=next_step,
            update={
                'notes': get_notes_from_tool_calls(supervisor_messages),
                'research_brief': state.get('research_brief', '')
            }
        )
    else:
        return Command(
            goto=next_step,
            update={
                'supervisor_messages': tool_messages,
                'raw_notes': all_raw_notes
            }
        )


# --- 도구 구성 -----------------------------------------------------------------
# 도구와 도구 목록을 가져온다
# supervisor_tools = get_tools()
supervisor_tools = get_tools(tool_names=['conduct_research_schema', 'research_complete_schema', 'reflection_tool'])

# --- 모델 및 파라미터 설정 --------------------------------------------------------
supervisor_model = init_chat_model(
    # model='ollama:gpt-oss:120b' 
    # model='groq:openai/gpt-oss-120b'  # (x)
    # model='google_genai:gemini-2.5-flash' 
    # model='anthropic:claude-sonnet-4-5'  
    model='openai:gpt-5'
)
supervisor_model_with_tools = supervisor_model.bind_tools(supervisor_tools)

# --- 시스템 상수 (system constants) ---------------------------------------------
# 하위 에이전트의 반복(think_tool + ConductResearchSchema) 한도 — 무한 루프 방지
# maximum number of tool call iterations for individual researcher agents
# this prevents infinite loops and controls research depth per topic
MAX_RESEARCHER_ITERATIONS = 6
 
# 동시에 띄울 하위 연구 조사 에이전트 수 한도(감독 에이전트 프롬프트 RESEARCH_SUPERVISOR_INSTRUCTION에 전달)
# maximum number of concurrent research agents the supervisor can launch
# this is passed to the RESEARCH_SUPERVISOR_INSTRUCTION에 to limit parallel research tasks
MAX_CONCURRENT_RESEARCHERS = 3

# --- 그래프 흐름 정의 ------------------------------------------------------------
# --- graph state
graph = StateGraph(SupervisorState)

# --- node
graph.add_node(
    node='Supervisor Agent', 
    action=SupervisorAgentNode(supervisor_model_with_tools)  # --- (new) -------
)  
graph.add_node('Supervisor Tools', supervisor_tools_node)  

# --- edge
graph.add_edge(START, 'Supervisor Agent')

# --- compile
supervisor_workflow = graph.compile()