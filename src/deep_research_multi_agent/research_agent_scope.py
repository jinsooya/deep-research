###############################################################################
### Deep Research Multi-Agent: 사용자 명확화 및 리서치 브리프 생성 모듈 ################
###############################################################################
# -----------------------------------------------------------------------------
# 이 모듈은 리서치 워크플로우의 스코핑(scoping) 단계를 구현한다.  
# 주요 단계:
# 1) 사용자의 요청이 리서치를 진행하기에 충분한 정보(맥락)를 포함하는지 평가한다.
# 2) 대화 내용을 바탕으로 상세한 리서치 브리프를 생성한다.

# 구조화된 출력(structured output)을 사용하여, 리서치 진행 가능 여부를
# 결정론적으로 판단하고 환각(hallucination)을 줄인다.
# -----------------------------------------------------------------------------

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_core.messages import get_buffer_string
from langchain_core.runnables import Runnable, RunnableConfig
from langchain.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model

from typing import Literal

from deep_research_multi_agent.prompts import (
    USER_CLARIFICATION,
    TRANSFORM_MESSAGES_INTO_RESEARCH_TOPIC
)
from deep_research_multi_agent.state_schemas_scope import AgentInputState, AgentState
from deep_research_multi_agent.data_schemas import UserIntentClarificationSchema, ResearchQuestionSchema
from deep_research_multi_agent.utils import get_today_str


# --- 노드 클래스 ----------------------------------------------------------------
class UserIntentClarificationNode:
    """
    사용자의 요청(intent)이 리서치를 진행하기에 충분한 맥락과 정보를 포함하는지 확인하는 노드 클래스  

    이 노드는 LLM을 구조화된 출력 스키마(`UserIntentClarificationSchema`)와 함께 사용하여  
    - 명확화 질문이 필요한 경우 -> 사용자에게 질문을 생성하고 워크플로우를 종료한다.  
    - 충분한 정보가 있는 경우 -> 리서치 브리프 생성 단계(`Research Brief Generator`)로 라우팅한다.  

    즉, 리서치 워크플로우의 시작 단계에서 사용자의 의도를 명확히 하여  
    후속 단계(브리프 생성, 조사, 보고서 작성 등)가 안정적으로 진행될 수 있도록 한다.
    """
    def __init__(self, runnable: Runnable) -> None:
        """
        UserIntentClarificationNode 초기화 메소드
        
        Args:
            runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)
        """
        # 구조화한 출력 스키마로 모델을 바인딩한다.
        # set up structured output model
        self.__runnable = runnable.with_structured_output(UserIntentClarificationSchema)  # (note) model_with_structured_output
    
    def __call__(self, state: AgentState, config: RunnableConfig | None = None) ->  Command[Literal['Research Brief Generator', '__end__']]:
    # def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
        """
        사용자의 요청이 리서치를 진행하기에 충분한 정보를 포함하는지 판단한다.

        구조화한 출력을 사용하여 결정론적 의사결정을 수행하고 환각을 방지한다.  
        충분한 정보가 없으면 명확화 질문을 생성하여 종료하고, 충분하면 브리프 생성 단계로 라우팅한다.

        Determine if the user's request contains sufficient information to proceed with research.
    
        Uses structured output to make deterministic decisions and avoid hallucination.
        Routes to either research brief generation or ends with a clarification question.
        
        Args:
            state (AgentState): 이전 상호작용을 포함한 현재 그래프 상태
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            Command[Literal['Research Brief Generator', '__end__']]:
                - 'Research Brief Generator': 리서치 브리프 생성 단계로 이동한다.
                - '__end__': 명확화 질문을 사용자에게 전달하고 종료한다.
                반환 객체에는 상태 업데이트용 메시지도 포함한다.
        """
        # 구조화한 출력 스키마로 모델을 바인딩한다.
        # set up structured output model
        # model_with_structured_output = model.with_structured_output(UserIntentClarificationSchema)
    
        # 명확화 지침과 함께 모델을 호출한다.
        # invoke the model with clarification instructions
        response = self.__runnable.invoke([
        # response = model_with_structured_output.invoke([
            HumanMessage(content=USER_CLARIFICATION.format(
                messages=get_buffer_string(messages=state['messages']),
                date=get_today_str()
            ))
        ])
    
        # 명확화 필요 여부에 따라 분기한다.
        # route based on clarification need
        if response.need_clarification:
            return Command(
                goto=END,
                update={'messages': [AIMessage(content=response.question)]},
            )
        else:
            return Command(
                goto='Research Brief Generator',
                update={'messages': [AIMessage(content=response.verification)]},
            )      

class ResearchBriefGenerationNode:
    """
    대화 이력을 입력으로 받아 리서치 브리프를 생성하는 노드 클래스
    
    구조화한 데이터 스키마(ResearchQuestionSchema)를 사용하여 일관된 형식의
    브리프를 생성하도록 모델을 바인딩한다.
    """
    def __init__(self, runnable: Runnable) -> None:
        """
        ResearchBriefGenerationNode의 초기화 메소드
        
        Args:
            runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)
        """
        # 구조화한 출력 스키마로 모델을 바인딩한다.
        # set up structured output model
        self.__runnable = runnable.with_structured_output(ResearchQuestionSchema)  # (note) model_with_structured_output
    
    def __call__(self, state: AgentState, config: RunnableConfig | None = None) ->  AgentState:
    # def __call__(self, state: MessagesState, config: RunnableConfig | None = None) ->  MessagesState:
        """
        대화 이력을 포괄적인 리서치 브리프로 변환한다.

        구조화한 출력을 사용하여 요구 형식을 보장하고, 효과적인 리서치를 위한
        필수 정보가 포함되도록 한다.
        
        Transform the conversation history into a comprehensive research brief.
    
        Uses structured output to ensure the brief follows the required format
        and contains all necessary details for effective research.
    
        Args:
            state (AgentState): 이전 상호작용을 포함한 현재 그래프 상태
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            AgentState: 업데이트한 그래프 상태로,
              - 'research_brief': 생성된 브리프 문자열
              - 'supervisor_messages': 감독 에이전트로 전달할 메시지 목록을 포함한다.
        """
        # 구조화한 출력 스키마로 모델을 바인딩한다.
        # set up structured output model
        # structured_output_model = model.with_structured_output(ResearchQuestionSchema)

        # 대화 이력으로부터 리서치 브리프를 생성한다.
        # generate research brief from conversation history
        response = self.__runnable.invoke([
        # response = structured_output_model.invoke([
            HumanMessage(content=TRANSFORM_MESSAGES_INTO_RESEARCH_TOPIC.format(
                messages=get_buffer_string(state.get('messages', [])),
                date=get_today_str()
            ))
        ])

        # 그래프 상태에 브리프를 저장하고 감독 에이전트로 전달할 메시지를 구성한다.
        # update state with generated research brief and pass it to the supervisor
        return {
            'research_brief': response.research_brief,
            'supervisor_messages': [HumanMessage(content=f'{response.research_brief}.')]
        }


# --- 모델 및 파라미터 설정 --------------------------------------------------------
model = init_chat_model(
    # model='ollama:gpt-oss:20b'   # (x) OutputParserException: Invalid json output
    # model='ollama:gpt-oss:120b'  # (x) OutputParserException: Invalid json output
    # model='groq:openai/gpt-oss-120b'  # (ok)
    # model='google_genai:gemini-2.5-flash'  # not working well
    model='anthropic:claude-sonnet-4-5'  # not working well
    # model='openai:gpt-5'
    # model='openai:gpt-4o'
)


# --- 그래프 흐름 정의 ------------------------------------------------------------
# --- graph state
graph = StateGraph(AgentState, input_schema=AgentInputState)

# --- node
graph.add_node('User Intent Clarifier', UserIntentClarificationNode(model))
graph.add_node('Research Brief Generator', ResearchBriefGenerationNode(model))

# --- edge
graph.add_edge(START, 'User Intent Clarifier')
graph.add_edge('Research Brief Generator', END)

# --- compile
scope_research_workflow = graph.compile()