from langchain_core.tools import BaseTool

from deep_research_multi_agent.tools.search_tools import tavily_search
from deep_research_multi_agent.tools.reflection_tool import reflection_tool


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
        'reflection_tool': reflection_tool
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