from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import BaseTool
from async_lru import alru_cache

from deep_research_multi_agent.tools.search_tools import tavily_search
from deep_research_multi_agent.tools.reflection_tool import reflection_tool
from deep_research_multi_agent.tools.supervisor_tools import ConductResearchSchema, ResearchCompleteSchema
from deep_research_multi_agent.tools.mcp import mcp_config

def get_tools(tool_names: list[str] | None = None) -> list[BaseTool]:
    """
    지정한 도구만 가져오거나, tool_names가 None이면 모든 도구 목록을 반환한다.

    Args:
        tool_names (list[str] | None): 포함할 도구 이름 리스트. None이면 모든 도구를 반환한다.

    Returns:
        list[BaseTool]: 도구 객체 목록이다.
    """
    
    # 기본 도구 딕셔너리를 구성한다.
    all_tools: dict[str, BaseTool] = {
        'tavily_search': tavily_search,
        'reflection_tool': reflection_tool,
        'conduct_research_schema': ConductResearchSchema,
        'research_complete_schema': ResearchCompleteSchema
    }
    if tool_names is None:
        return list(all_tools.values())
    
    # 지정한 이름만 필터링하여 반환한다.
    return [all_tools[name] for name in tool_names if name in all_tools]


def get_tools_by_name(tools: list[BaseTool] | None = None) -> dict[str, BaseTool]:
    """
    도구 목록을 도구 이름으로 매핑한 딕셔너리로 반환한다.

    Argss:
        tools (list[BaseTool] | None): 도구 객체 리스트. None이면 `get_tools` 함수 호출 결과를 사용한다.

    Returns:
        dict[str, BaseTool]: {도구이름: 도구객체} 형태의 매핑
    """
    # 입력이 없으면 기본 도구 목록을 가져온다.
    if tools is None:
        tools = get_tools()
    
    # 도구 이름을 키로 매핑하여 반환한다.
    return {tool.name: tool for tool in tools}


# --- Async-safe MCP Client (lazy singleton) -----------------------
@alru_cache(maxsize=1)
async def get_mcp_client() -> MultiServerMCPClient:
    """
    MCP 클라이언트를 '지연 초기화 + 단일 인스턴스'로 제공한다.

    왜 이렇게 구성하나?
    - MCP 클라이언트는 MCP 서버(@modelcontextprotocol/server-filesystem)와
      stdio 파이프(서브프로세스) 기반의 '지속 세션'을 유지한다.
    - 매 호출마다 새 클라이언트를 만들면 서버 프로세스가 중복 기동되고
      파이프가 꼬여 'Connection closed / Broken pipe / McpError'를 유발한다.
    - LangGraph처럼 노드가 순환 호출되거나 병렬 실행될 때, 단일 세션을
      재사용하지 않으면 비동기 이벤트 루프 충돌과 리소스 누수가 발생한다.

    설계 의도:
    - alru_cache(maxsize=1)로 비동기 환경에서 안전한 싱글톤을 만든다.
      첫 호출 시에만 실제 연결을 생성하고 이후에는 캐시된 인스턴스를 재사용한다.
    - 'lazy' 초기화이므로 필요한 시점에만 MCP 서버를 띄운다.
    - 주피터/스크립트/서비스 어디서든 동일한 호출 패턴(await get_mcp_client())으로 쓴다.

    사용 예:
        client = await get_mcp_client()
        mcp_tools = await client.get_tools()

    주의:
    - 세션 구성을 변경(mcp_config 변경)했거나 서버를 재기동해야 하면
      아래 reset_mcp_client()를 호출해 캐시를 비워 다시 생성한다.
    """
    return MultiServerMCPClient(mcp_config)


async def reset_mcp_client() -> None:
    """
    MCP 클라이언트를 안전 종료하고 싱글톤 캐시를 초기화한다.
    - 장시간 실행 중 세션을 재연결해야 할 때 사용한다.
    - 캐시를 비우면 다음 await get_mcp_client() 호출 시 새 인스턴스를 만든다.
    """
    client = await get_mcp_client()
    try:
        # MultiServerMCPClient 가 aclose 를 지원하면 우아하게 종료한다.
        if hasattr(client, "aclose"):
            await client.aclose()
    finally:
        # 캐시를 비워 다음 호출에서 재생성되도록 한다.
        get_mcp_client.cache_clear()