###############################################################################
### Deep Research Multi-Agent: 연구 조사 에이전트 모듈 ##############################
###############################################################################
# --- 모듈 임포트 ----------------------------------------------------------------
# 이 모듈은 복잡한 연구 조사 질문에 답하기 위해 반복적인 웹 검색과 정보 종합을 수행하는
# 연구 조사 에이전트를 구현한다.  
# This module implements a research agent capable of iterative web searches and 
# synthesis to answer complex research questions.
# -----------------------------------------------------------------------------

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, filter_messages
from langchain.chat_models import init_chat_model
from typing import Literal

from deep_research_multi_agent.state_schemas_research import ResearcherState, ResearcherOutputState
from deep_research_multi_agent.tools import get_tools, get_tools_by_name
from deep_research_multi_agent.utils import get_today_str
from deep_research_multi_agent.prompts import (
    RESEARCH_AGENT_INSTRUCTION,
    RESEARCH_CONDENSATION_INSTRUCTION,
    RESEARCH_CONDENSATION_HUMAN_MESSAGE
)


# --- 노드 클래스 ----------------------------------------------------------------
# --- 연구 조사 에이전트 노드 클래스 
class ResearchAgentNode:
    """
    연구 에이전트의 핵심 의사결정 노드 클래스  
    Node class for the research agent’s decision-making process

    이 노드는 연구 중간 단계에서 언어 모델(LLM)을 사용하여  
    현재의 연구 상태(`ResearcherState`)를 분석하고 다음 행동을 결정한다.  
    
    모델은 주어진 대화 및 툴 사용 이력을 기반으로 다음 중 하나를 선택한다:
    1. 더 많은 정보를 수집하기 위해 도구(tool)를 호출  
    2. 충분한 정보가 있다고 판단될 경우 최종 답변 생성  

    이 클래스는 LangChain의 Runnable 인터페이스와 LangGraph의 노드 아키텍처를 결합하여  
    연구 수행의 '판단' 단계(think / decide step)를 구현한다.  
    """
    def __init__(self, runnable: Runnable) -> None:
        """
        ResearchAgentNode의 초기화 메소드
        
        Args:
            runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)
            tools (list[BaseTool]): 에이전트가 사용할 수 있는 도구 객체 리스트  
                예를 들어, 웹 검색(`tavily_search`)이나 반성(reflection) 도구(`think_tool`) 등을 포함한다.
        """
        self.runnable = runnable  # (note) model_with_tools
    
    def __call__(self, state: ResearcherState, config: RunnableConfig | None = None) ->  ResearcherState:
    # def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
        """
        현재 상태를 분석하고 다음 액션을 결정한다.
    
        LLM은 현재 연구 상태를 기반으로 다음 중 하나를 수행한다.
        1. 추가 정보 수집을 위한 검색 도구 호출
        2. 수집한 정보를 기반으로 최종 답변 생성
    
        Analyze current state and decide on next actions.
    
        The model analyzes the current conversation state and decides whether to:
        1. Call search tools to gather more information
        2. Provide a final answer based on gathered information
    
        Returns updated state with the model's response.
        
        Args:
            state (ResearcherState): 이전 상호작용을 포함한 현재 그래프 상태
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            ResearcherState: 업데이트한 그래프 상태
        """
        return {
            'researcher_messages': [
                self.runnable.invoke(
                    [SystemMessage(content=RESEARCH_AGENT_INSTRUCTION)] 
                    + state['researcher_messages']
                )
            ]
        }
        
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


# --- 도구 처리 노드 클래스
class ToolsNode:
    """
    연구 워크플로우에서 도구 실행을 담당하는 노드 클래스  

    이 노드는 LLM이 이전 단계에서 요청한 도구 호출을 실제로 수행하고,  
    각 도구의 실행 결과를 `ToolMessage` 형태로 상태에 반영한다.  
    즉, 연구 에이전트의 '도구 실행 단계(tool execution step)'를 담당한다.

    Node class responsible for executing tool calls within the research workflow

    The node executes all tool calls generated by the LLM in the previous step  
    and records their outputs as `ToolMessage` objects in the state.  
    This represents the agent’s tool execution phase in the research workflow.
    """
    def __call__(self, state: ResearcherState, config: RunnableConfig | None = None) ->  ResearcherState:
    # def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
        """
        LLM이 요청한 도구 호출을 실행한다. 
        
        LLM의 마지막 응답에 포함된 모든 도구 호출을 실행하고,  
        결과를 `ToolMessage` 형태로 상태에 추가한다.
    
        Execute all tool calls from the previous LLM response.
    
        Executes all tool calls from the previous LLM responses.
        Returns updated state with tool execution results.
        
        Args:
            state (ResearcherState): 이전 상호작용을 포함한 현재 그래프 상태
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            ResearcherState: 업데이트한 그래프 상태
        """
        tool_calls = state['researcher_messages'][-1].tool_calls

        # 도구 호출 실행
        # execute all tool calls sequentially
        observations = []
        for tool_call in tool_calls:
            tool = tools_by_name[tool_call['name']]
            observations.append(tool.invoke(tool_call['args']))

        # 도구 실행 결과를 ToolMessage로 변환
        # convert tool outputs into ToolMessage objects
        tool_outputs = [
            ToolMessage(
                content=observation,
                name=tool_call['name'],
                tool_call_id=tool_call['id']
            ) for observation, tool_call in zip(observations, tool_calls)
        ]

        return {'researcher_messages': tool_outputs}

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
        a compressed summary suitable for the supervisor's decision-making.
    
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
            'compressed_research': str(response.content),
            'raw_notes': ['\n'.join(raw_notes)]
        }
         
         
# --- 도구 구성 -----------------------------------------------------------------
# 도구와 도구 목록을 가져온다
# tools = get_tools()
tools = get_tools(tool_names=['tavily_search', 'think_tool'])
tools_by_name = get_tools_by_name(tools)


# --- 모델 및 파라미터 설정 --------------------------------------------------------
model = init_chat_model(
    # model='ollama:gpt-oss:120b' 
    # model='groq:openai/gpt-oss-120b'  # (x)
    # model='google_genai:gemini-2.5-flash' 
    model='anthropic:claude-sonnet-4-5'  
    # model='openai:gpt-5'
)
model_with_tools = model.bind_tools(tools)

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
graph.add_node('Research Agent', ResearchAgentNode(model_with_tools))
graph.add_node('Tools', ToolsNode())
graph.add_node(
    node='Research Condensation', 
    action=ResearchCondensationNode(condensation_model)
)

# --- edge
graph.add_edge(START, 'Research Agent')
graph.add_conditional_edges(
    source='Research Agent',
    path=ResearchAgentNode.route,
    path_map={
        'tools': 'Tools', 
        'condense research': 'Research Condensation'
    }
)
graph.add_edge('Tools', 'Research Agent')
graph.add_edge('Research Condensation', END)

# --- compile
researcher_workflow = graph.compile()