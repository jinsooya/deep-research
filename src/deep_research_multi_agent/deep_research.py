###############################################################################
### Deep Research Multi-Agent: 연구 조사 에이전트 모듈 ##############################
###############################################################################
# --- 다중 에이전트 연구 조시 시스템 (Full Multi-Agent Research System) --------------
# 
# 이 모듈은 연구 시스템의 모든 구성 요소를 통합한다.
# - 사용자 요구 명확화 및 범위 정의  
# - 연구 브리프(Research Brief) 생성  
# - 다중 에이전트 기반 연구 수행 및 조정  
# - 최종 보고서 생성
# 
# 이 시스템은 초기 사용자 입력 단계부터 최종 보고서 작성 및 전달까지의 
# 전체 연구 워크플로우를 종합적으로 관리한다.
# -----------------------------------------------------------------------------
# This module integrates all components of the research system:
# - User clarification and scoping
# - Research brief generation  
# - Multi-agent research coordination
# - Final report generation
#
# The system orchestrates the complete research workflow from initial user
# input through final report delivery.
# -----------------------------------------------------------------------------
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import Runnable, RunnableConfig
from langchain.messages import HumanMessage
from langchain.chat_models import init_chat_model

from deep_research_multi_agent.utils import get_today_str
from deep_research_multi_agent.state_schemas_scope import AgentState, AgentInputState
from deep_research_multi_agent.research_agent_scope import UserIntentClarificationNode, ResearchBriefGenerationNode
from deep_research_multi_agent.research_multi_agent_supervisor import supervisor_workflow
from deep_research_multi_agent.prompts import FINAL_REPORT_GENERATION


# --- 노드 클래스 ----------------------------------------------------------------
# --- 최종 보고서 작성 에이전트 노드 클래스
class FinalReportGeneratorNode:
    """   
    최종 연구 보고서 생성 노드 클래스  

    LangGraph 기반 다중 연구 조사 시스템에서 **최종 결과 보고서를 작성하는 노드**다.  
    이 노드는 각 하위 연구 에이전트가 수행한 조사 결과(`notes`)를 종합하여  
    완전한 형태의 보고서를 생성한다.  

    주요 역할:
    - 모든 연구 결과(findings)를 통합하여 일관된 구조의 보고서 작성
    - 보고서 작성용 프롬프트(FINAL_REPORT_GENERATION)를 구성 및 실행
    - LangGraph 상에서 최종 출력 또는 상위 노드(supervisor)로 전달

    Key Responsibilities:
    1. Aggregate research findings from all sub-agents.
    2. Construct a final synthesis prompt with context and findings.
    3. Generate a structured final report through the language model.
    4. Return the completed report to the workflow graph.
    """
    def __init__(self, runnable: Runnable) -> None:
        """
        FinalReportGeneratorNode의 초기화 메소드
        
        Args:
            runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)            
        """
        self.runnable: Runnable = runnable  # writer_model
    
    async def __call__(self, state: AgentState, config: RunnableConfig | None = None):
    # async def __call__(self, state: MessagesState, config: RunnableConfig | None = None) -> MessagesState:
        """
        연구 결과를 종합하여 최종 보고서를 작성하는 비동기 호출 메서드  

        Synthesizes all research findings into a comprehensive final report
        
        Args:
            state (AgentState): 이전 상호작용을 포함한 현재 그래프 상태
                연구 브리프(`research_brief`)와 조사 결과(`notes`)를 포함한다.
            config (Optional[RunnableConfig]): 실행 시 설정 값으로, 메타데이터를 
                포함한 추가적인 설정을 할 수 있다.
 
        Returns:
            dict:
                - final_report (str): 완성된 최종 보고서 본문  
                - messages (list[str]): LLM 출력 로그를 포함한 메시지 리스트  
        """
        notes = state.get('notes', [])
    
        findings = '\n'.join(notes)

        final_report_prompt = FINAL_REPORT_GENERATION.format(
            research_brief=state.get('research_brief', ''),
            findings=findings,
            date=get_today_str()
        )
        
        final_report = await writer_model.ainvoke([HumanMessage(content=final_report_prompt)])
        
        return {
            'final_report': final_report.content, 
            # 'messages': ['Here is the final report: ' + final_report.content],
            'messages': ['최종 보고서가 완성되었습니다:\n' + final_report.content],
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

writer_model = init_chat_model(
    # model='ollama:gpt-oss:20b'   # (x) not working well (ERROR: error parsing tool call)
    # model='ollama:gpt-oss:120b', max_tokens=131_000  
    # model='groq:openai/gpt-oss-120b'       # not tested yet
    # model='google_genai:gemini-2.5-flash'  # not tested yet
    # model='anthropic:claude-sonnet-4-5'    # not tested yet# 
    model='openai:gpt-5'                   # not tested yet
)

# --- 그래프 흐름 정의 ------------------------------------------------------------
# --- graph state
graph = StateGraph(AgentState, input_schema=AgentInputState)

# --- node
graph.add_node(
    node='User Intent Clarifier', 
    action=UserIntentClarificationNode(model)
)
graph.add_node(
    node='Research Brief Generator', 
    action=ResearchBriefGenerationNode(model)
)
graph.add_node('Supervisor Subgraph', supervisor_workflow)
graph.add_node('Final Report Generator', FinalReportGeneratorNode(writer_model))

# --- edge
graph.add_edge(START, 'User Intent Clarifier')
graph.add_edge('Research Brief Generator', 'Supervisor Subgraph')
graph.add_edge('Supervisor Subgraph', 'Final Report Generator')
graph.add_edge('Final Report Generator', END)


# --- compile
deep_research_workflow = graph.compile()