# import os
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool, InjectedToolArg
from tavily import TavilyClient
from typing import Annotated, Literal
# from dotenv import load_dotenv

from deep_research_multi_agent.utils import (
    deduplicate_search_results, 
    process_search_results, 
    format_search_output
)

# Load environment variables
# load_dotenv()

# tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
tavily_client = TavilyClient()


summarization_model = init_chat_model(
    model='openai:gpt-5-mini'
)

def tavily_search_multiple(
    search_queries: list[str],
    max_results: int = 3,
    topic: Literal['general', 'news', 'finance'] = 'general',
    include_raw_content: bool = True,
) -> list[dict]:
    """
    여러 검색 쿼리에 대해 Tavily API를 사용하여 검색을 수행하는 함수  
    Perform search using Tavily API for multiple queries.

    Args:
        search_queries (list[str]):  
            실행할 여러 개의 검색 쿼리 목록  
            List of search queries to execute  
        max_results (int, optional):  
            각 쿼리당 반환할 최대 검색 결과 수 (기본값: 3)  
            Maximum number of results per query (default: 3)  
        topic (Literal["general", "news", "finance"], optional):  
            검색 결과를 필터링할 주제 (예: 'general', 'news', 'finance')  
            Topic filter for search results  
        include_raw_content (bool, optional):  
            원본 웹페이지 콘텐츠를 포함할지 여부 (기본값: True)  
            Whether to include raw webpage content (default: True)  

    Returns:
        list[dict]:  
            각 쿼리에 대한 검색 결과를 담은 딕셔너리 리스트  
            List of search result dictionaries
    """
    # Tavily API를 사용하여 각 쿼리를 순차적으로 검색 수행한다.
    # 참고: AsyncTavilyClient를 사용하면 이 단계를 병렬로 처리할 수 있다.
    # execute searches sequentially.
    # Note: yon can use AsyncTavilyClient to parallelize this step.
    search_docs = []
    for query in search_queries:
        # 각 검색 쿼리에 대해 Tavily API를 호출한다.
        # call Tavily API for each search query
        result = tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic
        )
        # 결과를 리스트에 추가한다.
        # append the result to the list
        search_docs.append(result)

    # 모든 쿼리의 검색 결과 리스트를 반환한다.
    # return the list of all search results
    return search_docs


# (caution) Docstring을 자동으로 파싱해서 함수의 매개변수(Args: 섹션)와 
#           실제 시그니처를 매칭하기 때문에 영어를 사용해야 한다.
#           그리고 : 뒤에 줄바꿈이 있으면 안되다.
@tool(parse_docstring=True)  
def tavily_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 3,
    topic: Annotated[Literal['general', 'news', 'finance'], InjectedToolArg] = 'general',
) -> str:
    """
    Tavily 검색 API를 사용해 콘텐츠 요약과 함께 검색 결과를 가져오는 도구 함수  
    Fetch results from Tavily search API with content summarization.

    Args:
        query (str): A single search query to execute  
        max_results (int, optional): Maximum number of results to return (default: 3)  
        topic (Literal['general', 'news', 'finance'], optional): Topic to filter results by ('general', 'news', 'finance')  

    Returns:
        str: Formatted string of search results with summaries
    """
    # 단일 쿼리를 내부 함수에서 처리할 수 있도록 리스트로 변환하여 검색 실행
    # execute search for single query
    search_results = tavily_search_multiple(
        search_queries=[query],  # convert single query to list for the internal function
        max_results=max_results,
        topic=topic,
        include_raw_content=True,
    )

    # 중복된 URL을 기준으로 검색 결과를 제거하여 중복 콘텐츠 처리 방지
    # deduplicate results by URL to avoid processing duplicate content
    unique_results = deduplicate_search_results(search_results)

    # 검색 결과를 요약하여 처리
    # process results with summarization
    summarized_results = process_search_results(summarization_model, unique_results)

    # 소비자(후속 에이전트나 노드)가 사용하기 좋은 형태로 포맷팅
    # format output for consumption
    return format_search_output(summarized_results)