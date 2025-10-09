from langchain_core.tools import tool


# (caution) Docstring을 자동으로 파싱해서 함수의 매개변수(Args: 섹션)와 
#           실제 시그니처를 매칭하기 때문에 영어를 사용해야 한다.
#           그리고 : 뒤에 줄바꿈이 있으면 안되다.
@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """
    연구 진행 상황과 의사결정에 대해 전략적으로 성찰(reflection)하기 위한 도구 함수  

    이 도구는 각 검색 이후에 결과를 분석하고, 다음 단계를 체계적으로 계획할 때 사용한다.
    이는 리서치 워크플로우 내에서 **품질 높은 의사결정을 위한 의도적 “사고 정지 단계”**를 제공한다. 

    사용 시점:
    - 검색 결과를 받은 후: 어떤 핵심 정보를 발견했는가?  
    - 다음 단계를 결정하기 전: 충분히 포괄적인 답변을 할 만큼 정보가 충분한가?  
    - 연구 공백을 평가할 때: 아직 부족한 핵심 정보는 무엇인가?  
    - 결론을 내리기 전: 지금 완전한 답변을 제공할 수 있는가?  

    성찰(reflection)은 다음 네 가지를 반드시 포함해야 한다 (Reflection should address):
    1. **현재 발견 내용 분석 (Current findings analysis)** – 지금까지 수집한 구체적 정보는 무엇인가?  
    2. **정보 공백 평가 (Gap assessment)** – 아직 부족한 핵심 정보는 무엇인가?  
    3. **품질 평가 (Quality evaluation)** – 충분한 근거와 사례가 수집되었는가?  
    4. **전략적 결정 (Strategic decision)** – 추가 검색이 필요한가, 아니면 이제 답변할 수 있는가?  
        
    Tool for strategic reflection on research progress and decision-making.
    
    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.
    
    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?
    
    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?
    
    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        str: Confirmation that reflection was recorded for decision-making
    """
    # return f'Reflection recorded: {reflection}'
    return f'Reflection이 기록되었습니다: {reflection}'