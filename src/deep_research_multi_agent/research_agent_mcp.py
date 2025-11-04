###############################################################################
### Deep Research Multi-Agent: 연구 조사 에이전트 모듈 (MCP 통합 버전) ################
###############################################################################
# --- 모듈 임포트 ----------------------------------------------------------------
# 이 모듈은 복잡한 연구 조사 질문에 답하기 위해 Model Context Protocol(MCP) 서버를 통해
# 로컬 파일 시스템에 접근하여 반복적인 문서 검색과 정보 종합을 수행하는 연구 조사 에이전트를 구현한다.
# This module implements a research agent capable of iterative document searches and 
# synthesis to answer complex research questions through Model Context Protocol (MCP) server integration.
# -----------------------------------------------------------------------------

import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import filter_messages
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from langchain.chat_models import init_chat_model
from typing import Literal

from deep_research_multi_agent.state_schemas_research import ResearcherState, ResearcherOutputState
from deep_research_multi_agent.tools import  get_tools_by_name, get_mcp_client, reflection_tool
from deep_research_multi_agent.utils import get_today_str
from deep_research_multi_agent.prompts import (
    RESEARCH_AGENT_MCP_INSTRUCTION,
    RESEARCH_CONDENSATION_INSTRUCTION,
    RESEARCH_CONDENSATION_HUMAN_MESSAGE
)


# --- 노드 클래스 ----------------------------------------------------------------
# --- 연구 조사 에이전트 노드 클래스 
class ResearchAgentNode:
    """
    연구 조사 에이전트의 핵심 의사결정 노드 클래스 (MCP 통합 버전)

    Model Context Protocol(MCP) 서버와 통신하여 파일 시스템 등
    외부 리소스를 활용한 연구를 수행하는 LangGraph 노드.

    주요 특징:
    - MCP 서버에서 도구 목록을 동적으로 조회하고 LangChain Runnable에 바인딩
    - 최초 1회만 도구를 로드하여 재사용 (지연 초기화)
    - 동시 실행 시에도 Lock을 통해 안전한 초기화 보장
    - LangGraph 환경에서 비동기적으로 LLM + MCP 도구 호출 가능
    
    Research Agent with MCP Integration

    This module implements a research agent that integrates with Model Context Protocol (MCP)
    servers to access tools and resources. The agent demonstrates how to use MCP filesystem
    server for local document research and analysis.

    Key features:
    - MCP server integration for tool access
    - Async operations for concurrent tool execution (required by MCP protocol)
    - Filesystem operations for local document research
    - Secure directory access with permission checking
    - Research compression for efficient processing
    - Lazy MCP client initialization for LangGraph Platform compatibility
    """
    def __init__(self, runnable: Runnable) -> None:
        """
        ResearchAgentNode의 초기화 메소드
        
        Args:
            runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)            
        """
        self.runnable: Runnable = runnable
        self.runnable_with_tools: Runnable | None = None  # 도구 바인딩된 Runnable 캐시
        self.tools_loaded: bool = False                   # 도구 초기화 여부
        self._init_lock = asyncio.Lock()                  # 동시 초기화 방지 Lock
    
    async def __call__(self, state: ResearcherState, config: RunnableConfig | None = None) ->  ResearcherState:
    # async def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
        """
        현재 상태(state)를 입력받아 LLM과 MCP 도구를 이용해 분석/응답한다.

        동작 순서:
        1. (최초 호출 시) MCP 서버에서 도구를 로드하고 모델에 바인딩
        2. 시스템 메시지 + 이전 대화 상태를 모델에 전달하여 실행
        3. 결과 메시지를 researcher_messages에 추가하여 반환
        
        Analyze current state and decide on tool usage with MCP integration.

        This node:
        1. Retrieves available tools from MCP server
        2. Binds tools to the language model
        3. Processes user input and decides on tool usage
    
        Returns updated state with the model's response.
        
        Args:
            state (ResearcherState): 이전 상호작용을 포함한 현재 그래프 상태
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            ResearcherState: 업데이트한 그래프 상태
        """
        # reflection_tool = get_tools(tool_names=['reflection_tool'])
        # --- 최초 1회 MCP 도구 로드 & 바인딩 (Lock으로 보호)
        #     첫 호출 시에만 MCP 도구 로드 & 바인딩 (이중 체크 잠금(double-checked locking) 패턴)
        if not self.tools_loaded:           # (1) 빠른 체크 — 락 없이 진입 방
            async with self._init_lock:     # 락 획득
                if not self.tools_loaded:   # (2) 다시 확인 — 진짜 아직이면 초기화
                    try:
                        # get available tools from MCP server
                        client    = await get_mcp_client()    # --- (new) -------
                        mcp_tools = await client.get_tools()  # --- (new) -------
                    except Exception as err:
                        raise RuntimeError(f'⚠️ MCP 도구 로드 중 오류 발생: {err}')
                    
                    # use MCP tools for local document access
                    tools = mcp_tools + [reflection_tool]
        
                    # initialize model with tool binding
                    self.runnable_with_tools = self.runnable.bind_tools(tools)  # (note) model_with_tools
                    self.tools_loaded = True

        # 모델 호출 (비동기 ainvoke 사용 권장)
        msg = await self.runnable_with_tools.ainvoke(
            [SystemMessage(
                content=RESEARCH_AGENT_MCP_INSTRUCTION.format(date=get_today_str())
            )]
            + state['researcher_messages']
        )

        return {'researcher_messages': [msg]}
        
    # --- conditional edge ----------------------------------------------------
    @staticmethod
    def route(state: ResearcherState) -> Literal['tools', 'condense research']:
        """
        연구를 계속 진행할지 또는 압축 단계로 이동할지 결정한다.
        
        LLM이 추가 도구 호출을 수행했는지 여부를 확인하여  
        - 도구 호출이 있다면 'tools'로 이동 (추가 검색)
        - 도구 호출이 없다면 'condense research' 로 이동 (연구 조사 종료)

    
        메시지 상태를 기반으로 'tools' 또는 'condense research'을 반환한다.
        
        Determine whether to continue research or move to compression

        Determines whether the agent should continue the research loop or provide
        a final answer based on whether the LLM made tool calls.
            
        Args:
            state (ResearcherState): 현재 메시지 상태
            
        Returns:
            Literal['tools', 'condense research']: 다음 노드 이름
            'tools': 도구 호출이 있다면 'tools'로 이동 (추가 검색)
            'condense research': 도구 호출이 없다면 'condense research' 로 이동 (연구 조사 종료)
            
            'tools': Continue to tool execution
            'condense research': Stop and compress research
                
        """
        messages = state['researcher_messages']
        last_message = messages[-1]

        # 도구 호출이 있으면 계속 진행
        # if the LLM makes a tool call, continue to tool execution
        if last_message.tool_calls:
            return 'tools'
        # 도구 호출이 없으면 압축 단계로 이동
        # otherwise, we have a final answer
        return 'condense research'


# # --- 도구 처리 노드 클래스
# class ToolsNode:
#     """
#     연구 조사 워크플로우에서 도구 실행을 담당하는 노드 클래스  

#     마지막 LLM 응답에 포함된 도구 호출들을 비동기(MCP)로 순차 실행하고,
#     결과를 ToolMessage로 변환해 상태에 추가한다.
#     """
#     async def __call__(self, state: ResearcherState, config: RunnableConfig | None = None) ->  ResearcherState:
#     # async def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
#         """
#         MCP 도구 호출을 실행하고 결과 메시지를 반환한다.

#         이 노드는:
#         1) 직전 메시지의 tool_calls를 읽고
#         2) MCP 툴(비동기) + reflection_tool(동기)을 적절히 실행한 뒤
#         3) ToolMessage 목록으로 변환해 researcher_messages에 기록한다.

        
#         Execute tool calls using MCP tools.

#         This node:
#         1. Retrieves current tool calls from the last message
#         2. Executes all tool calls using async operations (required for MCP)
#         3. Returns formatted tool results
    
#         Note: MCP requires async operations due to inter-process communication
#         with the MCP server subprocess. This is unavoidable.
        
#         Args:
#             state (ResearcherState): 이전 상호작용을 포함한 현재 그래프 상태
#             config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
#                 포함한 추가적인 설정을 할 수 있다.
 
#         Returns:
#             ResearcherState: 업데이트한 그래프 상태
#         """
#         # 직전 메시지에서 도구 호출 추출
#         tool_calls = state['researcher_messages'][-1].tool_calls or []
#         # reflection_tool = get_tools(tool_names=['reflection_tool'])
#         async def execute_tools():
#             """
#             모든 도구 호출을 실행한다. MCP 도구는 async, reflection_tool은 sync로 처리한다.
#             Execute all tool calls. MCP tools require async execution.
#             """
#             # MCP 서버에서 최신 도구 셋 가져오기
#             # get fresh tool references from MCP server
#             client = await get_mcp_client()
#             mcp_tools = await client.get_tools()
#             tools = mcp_tools + [reflection_tool]
#             # tools_by_name = {tool.name: tool for tool in tools}
#             tools_by_name = get_tools_by_name(tools)

#             # 순차 실행 (신뢰성 우선)
#             # execute tool calls (sequentially for reliability)
#             observations = []
#             for tool_call in tool_calls:
#                 tool = tools_by_name[tool_call['name']]
#                 if tool_call['name'] == 'reflection_tool':
#                     # 동기 (reflection_tool is sync, use regular invoke)
#                     observation = tool.invoke(tool_call['args'])  
#                 else: 
#                     # 비동기 (MCP tools are async, use ainvoke)
#                     observation = await tool.ainvoke(tool_call['args'])
#                 observations.append(observation)

#             # ToolMessage로 변환
#             # format results as tool messages
#             return [
#                 ToolMessage(
#                     content=observation,
#                     name=tool_call['name'],
#                     tool_call_id=tool_call['id'],
#                 )
#                 for observation, tool_call in zip(observations, tool_calls)
#             ]
    
#         messages = await execute_tools()
    
#         return {'researcher_messages': messages}

# --- 연구 조사 내용 압축 및 요약 노드 클래스
class ResearchCondensationNode:
    """
    연구 결과를 압축 및 요약하는 노드 클래스  

    이 노드는 연구 에이전트(Research Agent)의 마지막 단계에서 작동하며,  
    연구 중 수집된 모든 메시지(`AI` 응답, `Tool` 실행 결과 등)를 종합하여  
    **감독 에이전트(Supervisor Agent)** 가 검토하기 적합한 형태로  
    **압축한 요약(Condensed Summary)** 을 생성한다.  

    이를 통해 불필요한 중복이나 장황한 정보를 제거하고,  
    핵심 연구 결과만 남겨 다음 의사결정 단계(예: 보고서 작성, 검증 등)에 활용할 수 있다.  

    Node class for condensing and summarizing research findings  

    This node operates in the final stage of the research workflow.  
    It aggregates all collected messages — including AI outputs and tool observations —  
    and produces a **condensed summary** suitable for supervisor review and decision-making.  
    The process filters redundant or verbose information,  
    retaining only the essential findings for the next phase of research synthesis.
    """
    def __init__(self, runnable: Runnable) -> None:
        """
        ResearchAgentNode의 초기화 메소드
        
        Args:
            runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)
        """
        self.runnable = runnable  # (note) condensation_model
    
    def __call__(self, state: ResearcherState, config: RunnableConfig | None = None) ->  ResearcherState:
    # def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
        """
        연구 결과를 요약 및 압축한다.  
    
        모든 연구 메시지 및 도구 출력을 가져와 감독에이전트(supervisor)가 검토하기 
        적합한 형태로 압축 요약을 생성한다.
        
        Compress research findings into a concise summary.
    
        Takes all the research messages and tool outputs and creates
        a condensed summary suitable for the supervisor's decision-making.
    
        Args:
            state (ResearcherState): 이전 상호작용을 포함한 현재 그래프 상태
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            ResearcherState: 업데이트한 그래프 상태
        """
        # 압축용 시스템 프롬프트 구성
        instruction = RESEARCH_CONDENSATION_INSTRUCTION.format(date=get_today_str())
        messages = (
            [SystemMessage(content=instruction)] 
            + state.get('researcher_messages', []) 
            + [HumanMessage(content=RESEARCH_CONDENSATION_HUMAN_MESSAGE)]
        )
        # LLM을 호출하여 압축 수행
        # Perform summarization and compression
        response = self.runnable.invoke(messages)

        # 원 연구 노트를 추출한다 (AI 및 툴 메시지 기반)
        # extract raw notes from tool and AI messages
        raw_notes = [
            str(m.content) for m in filter_messages(
                state['researcher_messages'], 
                include_types=['tool', 'ai']
            )
        ]
        
        return {
            'condensed_research': str(response.content),
            'raw_notes': ['\n'.join(raw_notes)]
        }
         

# --- 노드 함수 -----------------------------------------------------------------
# NOTE: LLM을 사용하지 않으면 클래스 대신 함수로 정의해서 '클래스'와 '함수’로 이 둘의 차이를 구분한다. 
# 도구 처리 노드 함수       
async def tools_node(state: ResearcherState, config: RunnableConfig | None = None) ->  ResearcherState:
    """
    MCP 도구 호출을 실행하고 결과 메시지를 반환하는 노드 함수  

    마지막 LLM 응답에 포함된 도구 호출들을 비동기(MCP)로 순차 실행하고,
    결과를 ToolMessage로 변환해 상태에 추가한다.

    이 노드는:
    1) 직전 메시지의 tool_calls를 읽고
    2) MCP 툴(비동기) + reflection_tool(동기)을 적절히 실행한 뒤
    3) ToolMessage 목록으로 변환해 researcher_messages에 기록한다.
    
    Execute tool calls using MCP tools.

    This node:
    1. Retrieves current tool calls from the last message
    2. Executes all tool calls using async operations (required for MCP)
    3. Returns formatted tool results

    Note: MCP requires async operations due to inter-process communication
    with the MCP server subprocess. This is unavoidable.
    
    Args:
        state (ResearcherState): 이전 상호작용을 포함한 현재 그래프 상태
        config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
            포함한 추가적인 설정을 할 수 있다.

    Returns:
        ResearcherState: 업데이트한 그래프 상태
    """
    # 직전 메시지에서 도구 호출 추출
    tool_calls = state['researcher_messages'][-1].tool_calls or []

    async def execute_tools():
        """
        모든 도구 호출을 실행한다. MCP 도구는 async, reflection_tool은 sync로 처리한다.
        Execute all tool calls. MCP tools require async execution.
        """
        # MCP 서버에서 최신 도구 셋 가져오기
        # get fresh tool references from MCP server
        client = await get_mcp_client()
        mcp_tools = await client.get_tools()
        tools = mcp_tools + [reflection_tool]
        tools_by_name = {tool.name: tool for tool in tools}

        # 순차 실행 (신뢰성 우선)
        # execute tool calls (sequentially for reliability)
        observations = []
        for tool_call in tool_calls:
            tool = tools_by_name[tool_call['name']]
            if tool_call['name'] == 'reflection_tool':
                # 동기 (reflection_tool is sync, use regular invoke)
                observation = tool.invoke(tool_call['args'])  
            else: 
                # 비동기 (MCP tools are async, use ainvoke)
                observation = await tool.ainvoke(tool_call['args'])
            observations.append(observation)

        # ToolMessage로 변환
        # format results as tool messages
        return [
            ToolMessage(
                content=observation,
                name=tool_call['name'],
                tool_call_id=tool_call['id'],
            )
            for observation, tool_call in zip(observations, tool_calls)
        ]

    messages = await execute_tools()

    return {'researcher_messages': messages}


# --- 모델 및 파라미터 설정 --------------------------------------------------------
model = init_chat_model(
    # model='ollama:gpt-oss:120b' 
    # model='groq:openai/gpt-oss-120b'  # (x)
    # model='google_genai:gemini-2.5-flash' 
    model='anthropic:claude-sonnet-4-5'  
    # model='openai:gpt-5'
)

condensation_model = init_chat_model(
    model='openai:gpt-5', 
    # max_tokens=128_000
    #max_tokens=64_000
    # model='anthropic:claude-sonnet-4-5', 
    # max_tokens=128_000
    # max_tokens=64_000
)


# --- 그래프 흐름 정의 ------------------------------------------------------------
# --- graph state
graph = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

# --- node
graph.add_node(
    node='Research Agent with MCP', 
    action=ResearchAgentNode(model)  # --- (new) -------
)  
# graph.add_node('Tools', ToolsNode())  
graph.add_node('Tools', tools_node)  
graph.add_node(
    node='Research Condensation', 
    action=ResearchCondensationNode(condensation_model)
)  

# --- edge
graph.add_edge(START, 'Research Agent with MCP')
graph.add_conditional_edges(
    source='Research Agent with MCP',
    path=ResearchAgentNode.route,
    path_map={
        'tools': 'Tools', 
        'condense research': 'Research Condensation'
    }
)
graph.add_edge('Tools', 'Research Agent with MCP')
graph.add_edge('Research Condensation', END)

# --- compile
researcher_mcp_workflow = graph.compile()