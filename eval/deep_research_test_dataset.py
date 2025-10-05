from langchain_core.messages import HumanMessage, AIMessage

# --- Test Dataset ------------------------------------------------------------
# conversation_1 = [
#     HumanMessage(content="What's the best way to invest $50,000 for retirement?"),
#     AIMessage(content='Could you please provide some additional information to tailor the investment advice for your $50,000 retirement goal? Specifically:\n Your current age or desired retirement age\n Your risk tolerance (low, medium, high)\n Any preferences for investment types (e.g., stocks, bonds, mutual funds, real estate)\n Whether you are investing through a tax-advantaged account (e.g., IRA, 401(k)) or a regular brokerage account\n This will help me provide more personalized and relevant suggestions.'),
#     HumanMessage(content="I'm 25 and I want to retire by 45. My risk tolerance is high right now but I think will decrease over time. I have heard that stocks and ETFs are a good choice, but I'm open to anything. And I already have a 401k, but this would just be through a regular brokerage account.")
# ]

# conversation_2 = [
#     HumanMessage(content='I am looking for an apartment in NYC, can you help me?'),
#     AIMessage(content='Could you please specify your apartment preferences? For example:\n Desired neighborhoods or boroughs\n Number of bedrooms/bathrooms\n Budget range (monthly rent)\n Any amenities or must-have features\n Preferred move-in date\n This information will help me provide the most relevant apartment options in NYC.'),
#     HumanMessage(content="I'd prefer to live in Chelsea, Flatiron, or West Village. I'm looking for a 2 bed 2 bath, and I am looking for monthly rent below 7k. I'd like this to be a doorman building and have an in unit washer and dryer, but it's okay if there's no washer dryer. It's a plus if the building has a gym. And I'd like to move in in September 2025.")
# ]

# conversation_1 = [
#     HumanMessage(content='은퇴를 위해 5만 달러를 투자하려면 가장 좋은 방법이 무엇인가요?'),
#     AIMessage(content='맞춤 제안을 위해 몇 가지를 여쭙겠습니다:\n 1) 현재 나이와 목표 은퇴 나이\n 2) 현재 위험 성향(낮음/중간/높음)과 향후 변화 예상\n 3) 선호 투자자산(주식, 채권, ETF, 부동산 등)\n 4) 세후 일반 브로커리지인지, 세제혜택 계좌(예: IRA, 401k)인지'),
#     HumanMessage(content='현재 25세이고 45세에 은퇴하고 싶습니다. 지금은 위험 성향이 높지만 시간이 지나면 낮아질 것 같습니다. 주식과 ETF가 좋다고 들었지만 다른 것도 열려 있습니다. 이 돈은 일반 브로커리지 계좌로 투자합니다. 401k는 별도로 있습니다.')
# ]

# conversation_2 = [
#     HumanMessage(content='뉴욕에서 아파트를 구하려고 합니다. 도와주실 수 있나요?'),
#     AIMessage(content='선호 조건을 알려주시면 정확도가 높아집니다:\n 1) 선호 동네\n 2) 방/욕실 개수\n 3) 월세 예산\n 4) 도어맨, 세탁기 등 필수/우대 편의시설\n 5) 입주 희망 시기'),
#     HumanMessage(content='첼시, 플랫아이언, 웨스트빌리지를 선호합니다. 2베드 2배스가 필요하고, 월세는 7천 달러 미만이면 좋겠습니다. 도어맨 건물을 원하고, 세대 내 세탁기가 있으면 좋지만 필수는 아닙니다. 건물에 헬스장이 있으면 플러스입니다. 입주는 2025년 9월입니다.')
# ]

conversation_1 = [
    HumanMessage(content='모바일 앱의 무료→유료 구독 전환율을 올리기 위한 연구 브리프가 필요합니다.'),
    AIMessage(content='정확한 브리프 생성을 위해 확인드립니다:\n 1) 주요/보조 지표와 기준선\n 2) 대상 플랫폼·지역·코호트\n 3) 실험 변수(가격/페이월/메시지 등)와 셀 구성\n 4) 표본수·검정력·유의수준·기간·제외 기간\n 5) 가드레일 지표와 빈도 제한\n 6) 데이터/툴과 시작일·예산·개인화 허용 범위'),
    HumanMessage(content='기준선 전환율은 7일 내 무료→유료 3.2%입니다. 주요 지표는 Paid starts/MAU, 보조는 30일 유지율과 환불률입니다. iOS/Android, 한국과 미국만 포함합니다. 인앱 페이월과 이메일을 다룹니다. 페이월 디자인 4종과 미국 한정 가격 A/B(7.99 vs 8.49 USD)를 테스트합니다. 총 5개 테스트 셀에 80%, 컨트롤 10%, 장기 홀드아웃 10%로 나눕니다. 기간 28일이며 블랙프라이데이 주는 제외합니다. 최소 20만 명 표본, 유의수준 0.05, 검정력 0.8입니다. 가드레일은 환불률 +0.5%p 초과 상승 금지, 이메일은 주당 사용자당 2회 이하입니다. 개인화는 로컬라이징 배너만 허용합니다. 예산 5만 달러입니다. Amplitude와 Branch를 사용합니다. 시작일은 2025-10-15입니다.')
]

conversation_2 = [
    HumanMessage(content='2026년 봄학기 학부 기계학습 과목 교재를 선정하려고 합니다. 후보와 선정기준을 정리해 주세요.'),
    AIMessage(content='교육 맥락을 확인하겠습니다:\n 1) 대상 학년과 수학/코딩 배경\n 2) 강의 언어와 번역본 필요 여부\n 3) 예산과 판(개정 연도) 기준\n 4) 슬라이드/문제/온라인 자료 제공 조건\n 5) 수업 주차/시간과 평가 비율\n 6) 커버리지 우선순위(예: 커널 방법, SVM, 딥러닝 비중)'),
    HumanMessage(content='대상은 3~4학년이며 선형대수, 확률, 미적분을 이수했고 파이썬을 사용합니다. 강의는 한국어지만 번역본이 있으면 가산점이고 원서도 괜찮습니다. 학생당 6만원 이하가 예산입니다. 2022년 이후 개정판을 선호합니다. 공식 슬라이드·연습문제·노트 제공이 필요하고, 저자 자료의 수업 내 사용이 허용되어야 합니다. 학기는 15주, 주 2회, 회당 90분으로 총 30회입니다. 평가 비율은 과제 40, 중간 30, 기말 30입니다. 딥러닝은 4주만 다루고, 커널 방법과 SVM을 깊게 다룹니다.')
]


# --- Ground Truth Criteria ---------------------------------------------------
# criteria_1 = [
#     'Current age is 25',
#     'Desired retirement age is 45',
#     'Current risk tolerance is high',
#     'Interested in investing in stocks and ETFs',
#     'Open to forms of investment beyond stocks and ETFs'
#     'Investment account is a regular brokerage account',
# ]

# criteria_2 = [
#     'Looking for a 2 bed 2 bath apartment in Chelsea, Flatiron, or West Village',
#     'Monthly rent below 7k',
#     'Should be in a doorman building',
#     'Ideally have an in unit washer and dryer but not strict',
#     'Ideally have a gym but not strict',
#     'Move in date is September 2025'
# ]

# criteria_1 = [
#     '현재 나이 25세',
#     '목표 은퇴 나이 45세',
#     '현재 위험 성향 높음이며 시간이 지나면 낮아질 전망',
#     '주식과 ETF에 관심 있음',
#     '주식·ETF 이외의 투자에도 열려 있음',
#     '투자 계좌는 일반 브로커리지(과세계좌), 401k는 별도 보유'
# ]

# criteria_2 = [
#     '첼시·플랫아이언·웨스트빌리지 선호',
#     '2베드 2배스',
#     '월세 7천 달러 미만',
#     '도어맨 건물 필수',
#     '세대 내 세탁기는 우대이나 필수 아님',
#     '건물 내 헬스장은 우대',
#     '입주 시기는 2025년 9월'
# ]

criteria_1 = [
    '기준선 전환율: 7일 내 3.2%',
    '주요 지표: Paid starts/MAU; 보조 지표: 30일 유지율, 환불률',
    '대상: iOS/Android, 한국·미국',
    '채널: 인앱 페이월, 이메일',
    '실험: 페이월 4종 + 미국 가격 A/B(7.99 vs 8.49 USD)',
    '트래픽 분배: 테스트 80%(5셀), 컨트롤 10%, 장기 홀드아웃 10%',
    '기간: 28일, 블랙프라이데이 주 제외',
    '표본: ≥200,000명, α=0.05, power=0.8',
    '가드레일: 환불률 +0.5%p 초과 상승 불가; 이메일 빈도 주 2회/1인',
    '개인화: 로컬라이징 배너만 허용',
    '툴: Amplitude, Branch',
    '예산: 50,000 USD',
    '시작일: 2025-10-15'
]

criteria_2 = [
    '대상: 학부 3~4학년',
    '수학 배경: 선형대수·확률·미적분, 언어: 파이썬',
    '강의 언어 한국어, 번역본 있으면 가산점이나 원서도 허용',
    '학생당 예산 ≤ 6만원',
    '선호 개정 시점: 2022년 이후',
    '공식 슬라이드·연습문제·노트 제공 필요, 수업 내 사용 허용',
    '학기 구성: 15주, 주 2회, 회당 90분, 총 30회',
    '평가 비율: 과제 40, 중간 30, 기말 30',
    '커버리지: 커널 방법·SVM 심화, 딥러닝 4주만'
]