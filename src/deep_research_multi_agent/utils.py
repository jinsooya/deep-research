from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage
from datetime import datetime
from pathlib import Path
from typing import Any

from deep_research_multi_agent.data_schemas import SummarySchema
from deep_research_multi_agent.prompts import WEBPAGE_SUMMARY_INSTRUCTION


def get_today_str() -> str:
    """
    오늘 날짜를 사람이 읽기 좋은 문자열 형식으로 반환한다.  

    Returns:
        str: '요일 월 일, 연도' 형식의 문자열  
             예: 'Mon Jan 1, 2025'
    """
    # 현재 시간을 가져와 지정된 문자열 포맷으로 변환한다.
    return datetime.now().strftime('%a %b %-d, %Y')


def get_current_dir() -> Path:
    """
    현재 모듈의 디렉토리 경로를 가져오는 함수  
    Get the current directory of the module

    이 함수는 Jupyter Notebook과 일반 Python 스크립트 환경 모두에서 호환된다.  
    This function is compatible with both Jupyter notebooks and regular Python scripts.

    Returns:
        Path: 현재 디렉토리를 나타내는 Path 객체  
            Path object representing the current directory
    """
    try:
        # __file__ 변수가 존재할 경우 (일반 Python 스크립트 환경) 
        # When __file__ exists (standard Python script environment)
        return Path(__file__).resolve().parent  # 현재 파일의 실제 경로(Path(__file__).resolve().parent)를 반환
    except NameError:
        # __file__ 변수가 정의되어 있지 않을 경우 (예: Jupyter Notebook)
        # When __file__ is not defined (e.g., Jupyter Notebook)
        return Path.cwd()  # 현재 작업 디렉토리(Path.cwd())를 반환


def deduplicate_search_results(search_results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    검색 결과를 URL 기준으로 중복을 제거하는 함수  
    Deduplicate search results by URL to avoid processing duplicate content.

    이 함수는 여러 검색 쿼리 결과에서 동일한 URL을 가진 항목을 하나만 남기고 제거하여,  
    중복된 웹페이지 콘텐츠가 후속 처리 단계(예: 요약, 분석 등)에 다시 포함되지 않도록 한다.

    Args:
        search_results (list[dict[str, Any]]): Tavily API 등의 검색 결과 객체 리스트  
            각 항목은 'results' 키를 포함하며, 그 하위에 URL을 가진 결과 목록이 들어 있다.  
            List of search result dictionaries returned by the search API.

    Returns:
        dict[str, dict[str, Any]]:  
            URL을 키로 하고, 각 URL에 해당하는 고유한 검색 결과를 값으로 갖는 딕셔너리
            Dictionary mapping URLs to unique result entries
    """
    # URL을 기준으로 고유한 검색 결과만 남길 딕셔너리 초기화
    # initialize dictionary to store unique results by URL
    unique_results: dict[str, dict[str, Any]] = {}

    # 각 검색 응답(response)을 순회하며 결과(result) 확인
    # iterate over search responses
    for response in search_results:
        # 각 응답의 'results' 항목을 순회
        # iterate over results in each response
        for result in response['results']:
            url = result['url']
            # URL이 아직 추가되지 않았다면 unique_results에 저장
            # add to unique_results only if URL not seen before
            if url not in unique_results:
                unique_results[url] = result

    # URL 기준으로 중복이 제거된 검색 결과 반환
    # return deduplicated results
    return unique_results



def summarize_webpage_content(model: Runnable, webpage_content: str) -> str:
    """
    웹페이지의 원본 텍스트 콘텐츠를 요약 모델을 사용해 간결하게 요약하는 함수  
    Summarize webpage content using the configured summarization model

    이 함수는 웹페이지의 원문(`webpage_content`)을 입력받아,  
    요약 모델(`summarization_model`)을 통해 핵심 요약(summary)과 주요 발췌문(key excerpts)을 생성한다.  
    구조화한 출력(`SummarySchema` Pydantic 스키마)을 활용하여 일관된 형식의 요약 결과를 반환한다.

    Args:
        runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)
        webpage_content (str): 요약할 원본 웹페이지 콘텐츠  
                               Raw webpage content to summarize  

    Returns:
        str: 요약 결과와 주요 인용구를 포함한 구조화한 문자열  
             실패 시, 원본 콘텐츠의 처음 1000자까지만 잘라 반환한다.
             Formatted summary string with key excerpts included.  
    """
    try:
        # 구조화한 출력 모델을 설정한다.
        # set up structured output model for summarization
        model_with_structure = model.with_structured_output(SummarySchema)

        # 요약 모델을 실행하여 결과를 생성한다.
        # generate summary using summarization model
        summary = model_with_structure.invoke([
            HumanMessage(content=WEBPAGE_SUMMARY_INSTRUCTION.format(
                webpage_content=webpage_content,
                date=get_today_str()
            ))
        ])

        # 요약 결과를 명확한 XML-like 구조로 포맷팅한다.
        # format summary output with clear structure for readability
        formatted_summary = (
            f'<summary>\n{summary.summary}\n</summary>\n\n'
            f'<key_excerpts>\n{summary.key_excerpts}\n</key_excerpts>'
        )

        return formatted_summary

    except Exception as e:
        # 오류 발생 시 로그 출력 후, 원문 일부를 반환한다.
        # handle errors gracefully, return truncated original content
        print(f'ERROR: Failed to summarize webpage: {str(e)}')
        return (
            webpage_content[:1000] + '...'
            if len(webpage_content) > 1000
            else webpage_content
        )


def process_search_results(
    runnable: Runnable, 
    unique_results: dict[str, dict[str, Any]]
) -> dict[str, dict[str, str]]:
    """
    검색 결과를 요약하여 처리하는 함수  
    Process search results by summarizing content where available.

    이 함수는 중복을 제거한 검색 결과를 입력받아,  
    각 결과의 원본 콘텐츠('raw_content')가 존재하면 요약을 수행하고,  
    요약한 내용을 포함한 새 결과 딕셔너리를 반환한다.  
    원본 콘텐츠가 없으면, 기본 'content' 필드를 그대로 사용한다.

    Args:
        runnable (Runnable): LangChain 실행 가능 객체 (예: 언어 모델)
        unique_results (dict[str, dict[str, Any]]):  
            URL을 키로 하고, 각 URL에 대한 고유한 검색 결과 데이터를 값으로 갖는 딕셔너리
            Dictionary of unique search results, keyed by URL

    Returns:
        dict[str, dict[str, str]]:  
            요약된 콘텐츠를 포함하는 처리한 검색 결과 딕셔너리
            Dictionary of processed results with summaries
    """
    # 요약한 검색 결과를 저장할 딕셔너리 초기화
    # initialize dictionary to store summarized results
    summarized_results: dict[str, dict[str, str]] = {}

    # 각 URL과 해당 검색 결과를 순회
    # iterate over URLs and their corresponding results
    for url, result in unique_results.items():
        # raw_content가 없으면 기본 content 사용
        # use existing content if no raw_content available
        if not result.get('raw_content'):
            content = result['content']
        else:
            # raw_content가 있으면 요약 수행
            # summarize raw content for better downstream processing
            content = summarize_webpage_content(runnable, result['raw_content'])

        # 요약 또는 원문 콘텐츠와 제목(title)을 저장
        # store summarized content and title in output dictionary
        summarized_results[url] = {
            'title': result['title'],
            'content': content
        }

    # 요약한 결과 반환
    # return processed (summarized) results
    return summarized_results    


def format_search_output(summarized_results: dict[str, dict[str, str]]) -> str:
    """
    요약한 검색 결과를 구조화한 문자열로 포맷팅하는 함수  
    Format search results into a well-structured string output

    이 함수는 `process_search_results()`에서 처리한 검색 결과 딕셔너리를 입력받아,  
    각 출처(source)별 제목, URL, 요약문을 명확히 구분하여 사람이 읽기 쉬운 형식으로 반환한다.  
    결과가 없으면, 안내 메시지를 반환한다.

    Args:
        summarized_results (dict[str, dict[str, str]]):  
            URL을 키로 하고, 각 검색 결과의 제목('title')과 요약('content')을 매핑값으로 갖는 딕셔너리 
            Dictionary of processed search results containing title and content fields

    Returns:
        str: 각 출처별로 구분한 명확한 구조의 검색 결과 문자열
             Formatted string of search results with clear source separation
    """
    # 검색 결과가 비어 있으면 안내 메시지 반환
    # return a message if no results are available
    if not summarized_results:
        return (
            'No valid search results found. '
            'Please try different search queries or use a different search API.'
        )

    # 포맷팅된 문자열을 초기화
    # initialize formatted output string
    formatted_output = 'Search results:\n\n'

    # 각 검색 결과를 순회하며 제목, URL, 요약을 포맷팅
    # iterate over results and format with clear source separation
    for i, (url, result) in enumerate(summarized_results.items(), 1):
        formatted_output += f'\n\n--- SOURCE {i}: {result['title']} ---\n'
        formatted_output += f'URL: {url}\n\n'
        formatted_output += f'SUMMARY:\n{result['content']}\n\n'
        formatted_output += '-' * 80 + '\n'

    # 최종 포맷 문자열 반환
    # return formatted string
    return formatted_output 