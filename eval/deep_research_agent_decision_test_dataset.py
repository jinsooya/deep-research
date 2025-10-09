from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

# # Scenario 1: Agent should CONTINUE - has insufficient/irrelevant information + think_tool realizes more research needed
# messages_should_continue = [
#     HumanMessage(content='What are the top coffee shops in San Francisco based on coffee quality?'),
#     AIMessage(
#         content="I'll search for information about top coffee shops in San Francisco focusing on coffee quality.",
#         tool_calls=[{
#             'name': 'tavily_search',
#             'args': {
#                 'query': 'coffee shops San Francisco popular locations'
#             },
#             'id': 'call_continue_search_001',
#             'type': 'tool_call'
#         }]
#     ),
#     # tavily Search provides generic cafe information - NOT focused on coffee quality
#     ToolMessage(
#         content='Search results show popular San Francisco cafes: Blue Bottle Coffee has great wifi and ambiance, Philz Coffee is known for custom blends and friendly service, Café Reveille has multiple locations with good pastries and laptop-friendly spaces. Ritual Coffee offers cozy seating and is popular with students.',
#         tool_call_id='call_continue_search_001'
#     ),
#     # agent uses think_tool to reflect and realizes the search results are insufficient
#     AIMessage(
#         content='Let me use the think_tool to analyze these search results and determine next steps.',
#         tool_calls=[{
#             'name': 'think_tool',
#             'args': {
#                 'reflection': "Analysis of search results: The information I found focuses on general cafe features like wifi, ambiance, custom blends, and seating - but lacks specific coffee quality metrics. The user specifically asked for evaluation based on coffee quality, which would require expert reviews, professional ratings, specialty certifications, or quality-focused customer feedback. I need to search specifically for coffee quality assessments, Coffee Review scores, specialty coffee credentials, or expert evaluations of SF coffee shops. The current information is insufficient to answer the user's question about coffee quality."
#             },
#             'id': 'call_continue_think_001',
#             'type': 'tool_call'
#         }]
#     ),
#     # think_tool response identifies the gap and need for more targeted research
#     ToolMessage(
#         content="Reflection recorded: Analysis of search results: The information I found focuses on general cafe features like wifi, ambiance, custom blends, and seating - but lacks specific coffee quality metrics. The user specifically asked for evaluation based on coffee quality, which would require expert reviews, professional ratings, specialty certifications, or quality-focused customer feedback. I need to search specifically for coffee quality assessments, Coffee Review scores, specialty coffee credentials, or expert evaluations of SF coffee shops. The current information is insufficient to answer the user's question about coffee quality.",
#         tool_call_id='call_continue_think_001'
#     )
# ]

# # Scenario 2: Agent should STOP - has comprehensive coffee quality information + think_tool reflection
# messages_should_stop = [
#     HumanMessage(content='What are the top coffee shops in San Francisco based on coffee quality?'),
#     AIMessage(
#         content="I'll research San Francisco coffee shops specifically focusing on coffee quality assessments and expert reviews.",
#         tool_calls=[{
#             'name': 'tavily_search',
#             'args': {
#                 'query': 'best coffee quality San Francisco specialty coffee expert reviews Coffee Review ratings 2024'
#             },
#             'id': 'call_stop_search_001', 
#             'type': 'tool_call'
#         }]
#     ),
#     # this ToolMessage provides COMPREHENSIVE coffee quality information - sufficient to answer the question
#     ToolMessage(
#         content='''Coffee quality research for San Francisco reveals top establishments based on expert reviews and specialty coffee credentials:

# **Top Quality-Focused Coffee Shops:**
# 1. **Sightglass Coffee** - Coffee Review score 94/100, known for single-origin beans and precise roasting techniques. Featured in Bon Appétit's 'Best Coffee in America' list for exceptional coffee quality.

# 2. **Saint Frank Coffee** - Ranked #3 coffee shop in America by The Daily Meal based on coffee quality. 4.3/5 Yelp rating with reviews specifically praising 'exceptional bean quality' and 'perfect extraction.'

# 3. **Ritual Coffee Roasters** - Specialty Coffee Association member, direct trade relationships, consistently rated 4.4/5 on Google with reviews highlighting 'superior coffee taste' and 'expert barista skills.'

# 4. **Blue Bottle Coffee** - Third-wave coffee pioneer, Coffee Review scores averaging 90+/100, known for rigorous quality control and fresh roasting practices.

# 5. **Four Barrel Coffee** - Local roaster with Coffee Review scores 88-92/100, praised by industry experts for 'exceptional coffee quality' and innovative brewing methods.

# **Quality Indicators Found:**
# - Coffee Review professional scores (88-94/100 range)
# - Specialty Coffee Association certifications
# - Direct trade/single-origin sourcing
# - Expert recognition from food publications
# - Customer reviews specifically mentioning coffee taste and quality

# This provides a comprehensive assessment of SF coffee shops based specifically on coffee quality rather than ambiance or service.''',
#         tool_call_id='call_stop_search_001',
#     ),
#     # Agent now uses think_tool to reflect on the search results
#     AIMessage(
#         content='Let me reflect on the search results using the think_tool to assess whether I have sufficient information.',
#         tool_calls=[{
#             'name': 'think_tool',
#             'args': {
#                 'reflection': 'Analysis of search results: I found comprehensive coffee quality information for SF coffee shops including: 1) Professional Coffee Review scores (88-94/100), 2) Expert rankings from reputable publications, 3) Specialty Coffee Association certifications, 4) Specific quality indicators (single-origin, roasting techniques, extraction methods), 5) Five top-rated establishments with detailed quality assessments. This covers all aspects requested: expert reviews, customer ratings, specialty certifications. I have enough information to provide a well-supported ranking based specifically on coffee quality. No additional searches needed - I should provide my comprehensive answer now.'
#             },
#             'id': 'call_think_001',
#             'type': 'tool_call'
#         }]
#     ),
#     # think_tool response confirming reflection was recorded
#     ToolMessage(
#         content='Reflection recorded: Analysis of search results: I found comprehensive coffee quality information for SF coffee shops including: 1) Professional Coffee Review scores (88-94/100), 2) Expert rankings from reputable publications, 3) Specialty Coffee Association certifications, 4) Specific quality indicators (single-origin, roasting techniques, extraction methods), 5) Five top-rated establishments with detailed quality assessments. This covers all aspects requested: expert reviews, customer ratings, specialty certifications. I have enough information to provide a well-supported ranking based specifically on coffee quality. No additional searches needed - I should provide my comprehensive answer now.',
#         tool_call_id='call_think_001'
#     )
# ]

# 시나리오 1: Agent should CONTINUE - 정보가 일반적/불충분 -> think_tool로 추가 연구 결정
# Scenario 1: Agent should CONTINUE - insufficient information for research report
# 아직 충분한 정보가 없으며, think_tool이 “더 깊은 조사가 필요함”을 인식
messages_should_continue = [
    HumanMessage(content='AI 에이전트 기반 결제 시스템의 최신 동향에 대한 연구 보고서를 원합니다.'),
    AIMessage(
        content='AI 에이전트 기반 결제 동향을 조사하기 위해 먼저 전반적 기사와 보도자료를 검색하겠습니다.',
        tool_calls=[{
            'name': 'tavily_search',
            'args': {
                'query': 'AI agent payment systems trends news announcements partnerships 2024 2025'
            },
            'id': 'call_continue_search_001',
            'type': 'tool_call'
        }]
    ),
    # 첫 검색 결과: 일반적 이슈 나열(객관 요약만, 판단 없음)
    ToolMessage(
        content=(
            '검색 결과: 여러 기업의 AI 기능 탑재 결제 서비스 발표와 파트너십 보도자료가 확인됩니다. '
            '예: 대형 PSP의 챗봇 결제 안내 기능 출시, 일부 은행에서 자동 납부/고객지원에 AI 적용, '
            "핀테크 스타트업이 '자율 결제 플로우' 또는 '스마트 체크아웃' 기능을 소개. "
            '컨퍼런스 요약에는 전자상거래/소매에서의 시범 적용 사례가 포함됩니다.'
        ),
        tool_call_id='call_continue_search_001'
    ),
    # 에이전트가 think_tool을 사용하여 검색 결과를 검토한 후, 정보가 불충분하다는 것을 인식함
    AIMessage(
        content='검색 결과를 검토한 뒤, 다음 단계를 결정하기 위해 think_tool을 사용하겠습니다.',
        tool_calls=[{
            'name': 'think_tool',
            'args': {
                'reflection': (
                    '분석: 현재 결과는 보도자료 수준의 일반 정보 중심으로, 최신 동향 보고서에 필요한 '
                    '정량 데이터(시장 규모/성장률), 기술 아키텍처 변화(에이전트형 결제 오케스트레이션, '
                    '리스크·KYC 자동화), 규제·보안 이슈(PCI-DSS, AML/PSD2, AI 거버넌스), '
                    '주요 사례(대형 카드사/네트워크/게이트웨이/지갑)의 구체적 성과지표가 부족함. '
                    '계획: 산업 리포트/백서/규제 문서/테크 블로그를 타겟으로 재검색 필요. '
                    "예) 'agentic payments architecture whitepaper 2025', "
                    "'AI payment risk orchestration case study', "
                    "'real-time authorization agent PSD2 AML 2024 site:europa.eu'."
                )
            },
            'id': 'call_continue_think_001',
            'type': 'tool_call'
        }]
    ),
    # think_tool이 ‘reflection 내용을 기록하였음’을 확인하는 응답을 반환함
    ToolMessage(
        content=(
            'Reflection이 기록되었습니다: 분석에 따라 보다 구조화된 출처(산업 리포트, 규제 문서, 기술 백서)를 '
            '대상으로 재검색을 진행합니다.'
        ),
        tool_call_id='call_continue_think_001'
    )
]


# 시나리오 2: Agent should STOP - 포괄적/충분한 정보 확보 -> think_tool로 종료 판단
# Scenario 2: Agent should STOP - comprehensive information gathered
# 충분하고 구체적인 산업 분석 및 기술 동향 데이터를 확보함
messages_should_stop = [
    HumanMessage(content='AI 에이전트 기반 결제 시스템의 최신 동향에 대한 연구 보고서를 원합니다.'),
    AIMessage(
        content='최신 동향을 정리하기 위해 시장 규모/기술 아키텍처/규제·보안/주요 사례를 포함한 자료를 검색하겠습니다.',
        tool_calls=[{
            'name': 'tavily_search',
            'args': {
                'query': (
                    'agentic AI payments market size CAGR 2024 2025 architecture orchestration '
                    'risk KYC AML regulatory PSD2 PCI-DSS case study network gateway wallet report'
                )
            },
            'id': 'call_stop_search_001',
            'type': 'tool_call'
        }]
    ),
    # 포괄적 결과(정량+정성 지표, 기술/규제/사례 포함) — 답변에 충분
    ToolMessage(
        content='''AI 에이전트 기반 결제 시스템 최신 동향(요약 수집 결과):

**시장/투자 동향**
- 에이전트형 AI 도입 가속: 결제 승인·리스크 평가·KYC/AML·분쟁 처리 자동화 활용 증가.
- 여러 시장조사에서 결제·금융 도메인의 에이전트형 AI 투자가 고성장(CAGR 30~45%대) 전망으로 집계.

**기술 아키텍처 트렌드**
- **오케스트레이션 레이어**: LLM/도메인 에이전트가 라우팅·재시도·SCA(강화인증) 플로우를 동적으로 제어.
- **리스크·컴플라이언스 에이전트**: 트랜잭션 맥락 분석, 이상 탐지, 규칙+ML 하이브리드 스코어링 자동화.
- **데이터 파이프라인**: 이벤트 스트리밍(실시간 피처), 벡터검색(서식 문서/규제 문서 참조), 정책 엔진 통합.
- **안전장치**: 도구 호출 가드, 금전/한도 정책, 인간 검토(HITL) 인터럽트, 재현 가능한 감사 로그.

**규제/보안**
- **PCI-DSS/PSD2/SCA, AML/KYC** 요구 정렬: 프라이버시·지불 카드 데이터 보호, 실시간 모니터링 강화.
- **AI 거버넌스**: 모델 책임성, 설명가능성, 편향 완화, 감사 추적(에이전트 행동 로그) 요구 증대.

**주요 적용 사례(요약)**
- 카드 네트워크/게이트웨이: 실시간 승인률 최적화 에이전트(A/B 라우팅, 재시도, MCC/지역별 정책).
- PSP/지갑: 스마트 체크아웃/구독 결제 어시스트, 분쟁 처리 자동 응대, 상점주 대시보드 요약 에이전트.
- 은행/핀테크: KYB/KYC 자동 수집·요약, 고위험 거래 에스컬레이션, 규제 질의 자동 대응.

**평가 지표(실무에서 보고되는 KPI 예)**
- 승인률(Authorization Rate) ↑, 거절률/차지백율/오탐률 ↓
- SCA 완료율·시간, 평균 해결 시간(MTTR), 운영비 절감(%)
- 규제 대응 시간 단축, 감사 적합성(증빙 자동화) 개선

**기술 스택 예시**
- 모델: 전이용 LLM + 소규모 도메인 모델 조합, 함수/툴 콜 기반 워크플로우
- 인프라: 이벤트 스트림(Kafka 등), 피처 스토어, 정책/룰 엔진, 벡터DB, 비동기 태스크 큐
- 가드레일: 정책 프롬프트, 금전 한도/승인 정책, 휴리스틱 필터, 인간 검토 인터럽트

위 자료는 시장 규모 관측치, 기술 백서, 규제 가이드, 사례 중심 블로그/리포트 등에서 종합된 최신 동향으로, 정량/정성 지표와 기술·규제·사례가 구비되어 최종 보고서 작성에 충분합니다.''',
        tool_call_id='call_stop_search_001'
    ),
    # 에이전트가 think_tool을 사용하여 검색 결과를 검토하고, 정보의 충분성과 다음 단계를 평가함
    AIMessage(
        content='수집 결과가 충분한지 확인하기 위해 think_tool로 최종 점검을 진행하겠습니다.',
        tool_calls=[{
            'name': 'think_tool',
            'args': {
                'reflection': (
                    '분석: 시장/기술/규제/사례/KPI까지 모두 확보되어 종합 보고서 작성에 필요한 핵심 요소가 충족됨. '
                    '특히 오케스트레이션 구조, 리스크·규제 에이전트, 거버넌스, 대표 KPI와 사례가 포함되어 요청 범위를 포괄. '
                    '결론: 추가 검색 없이 최종 보고서를 작성해도 충분함.'
                )
            },
            'id': 'call_think_001',
            'type': 'tool_call'
        }]
    ),
    # think_tool이 ‘reflection 내용을 기록하였음’을 확인하는 응답을 반환함
    ToolMessage(
        content=(
            'Reflection이 기록되었습니다: 수집된 동향 정보가 포괄적이므로 추가 검색 없이 최종 보고서를 작성합니다.'
        ),
        tool_call_id='call_think_001'
    )
]