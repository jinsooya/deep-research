'''
Email evaluation dataset with ground truth classifications.
'''

# --- 일반적인 답장 이메일 -------------------------------------------------------------
STANDARD_EMAIL = {
   'from': '강감찬 <gamchan.kang@a2i.com>',
   'to': '홍길동 <gildong.hong@a2i.com>',
   'subject': 'API 문서에 대한 간단한 질문',
   'body': '''안녕하세요 제임스,

새로운 인증 서비스의 API 문서를 검토하던 중 몇 개의 엔드포인트가 명세서에서 누락된 것 같아서 연락드립니다. \
이것이 의도적인 것인지 아니면 문서를 업데이트해야 하는지 확인해주실 수 있나요?

구체적으로는 다음 엔드포인트들입니다:
- /auth/refresh
- /auth/validate

감사합니다!
헨리
'''
}

# --- 일반적인 알림 이메일 -------------------------------------------------------------
NOTIFICATION_EMAIL = {
    'from': '시스템 관리자 <sysadmin@a2i.com>',
    'to': '개발팀 <dev@a2i.com>',
    'subject': '정기 점검 - 데이터베이스 중단',
    'body': '''안녕하세요 팀 여러분,

오늘 밤 오전 2시부터 4시까지 운영 데이터베이스의 정기 점검을 실시한다는 것을 알려드립니다. \
이 시간 동안 모든 데이터베이스 서비스가 중단됩니다.

이에 맞춰 업무 계획을 세우시고 이 시간대에 중요한 배포가 예정되지 않도록 해주세요.

감사합니다,

시스템 관리자 팀
'''
}

# --- 태스트 데이터셋 예시들 -------------------------------------------------------------
email_input_1 = {
    'from': '강감찬 <gamchan.kang@a2i.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': 'API 문서에 대한 간단한 질문',
    'body': '''안녕하세요 앤디,

새로운 인증 서비스의 API 문서를 검토하던 중 몇 개의 엔드포인트가 스펙에서 누락된 것 같아 보였습니다. \
이것이 의도적인 것인지 아니면 문서를 업데이트해야 하는지 명확히 해주실 수 있나요?

구체적으로 다음을 찾고 있습니다:
- /auth/refresh
- /auth/validate

감사합니다!
헨리
'''
}

email_input_2 = {
    'from': '마케팅팀 <marketing@a2i.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '새로운 회사 뉴스레터 발행',
    'body': '''안녕하세요 앤디,

회사 뉴스레터의 최신호가 인트라넷에서 이용 가능합니다. 이번 달에는 2분기 결과, \
향후 팀 빌딩 활동, 그리고 직원 스포트라이트에 관한 기사가 포함되어 있습니다.

시간이 있을 때 확인해 주세요!

좋은 하루 되세요.
마케팅팀
'''
}

email_input_3 = {
    'from': '시스템 관리자 <sysadmin@a2i.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '예정된 유지보수 - 데이터베이스 다운타임',
    'body': '''안녕하세요 앤디,

오늘 밤 새벽 2시부터 4시까지(EST) 프로덕션 데이터베이스에 예정된 유지보수를 진행할 \
예정이라는 것을 알려드립니다. 이 시간 동안 모든 데이터베이스 서비스가 사용 불가능합니다.

업무를 그에 맞게 계획하시고 이 기간 동안 중요한 배포가 예정되지 않도록 확인해 주세요.

감사합니다.
시스템 관리자 팀
'''
}

# email_input_4 = {
#     'from': '이순신 <yisunsin@client.com>',
#     'to': '온톨리지 <ontology@a2i.com>',
#     'subject': '세무 신고 시즌 통화 일정 잡기',
#     'body': '''앤디님,

# 세금 신고 시즌이 다시 돌아왔습니다. \
# 올해 세금 계획 전략을 논의하기 위해 전화 상담을 예약하고 싶습니다. \
# 비용을 절약할 수 있는 몇 가지 제안이 있습니다.

# 다음 주에 시간이 있으신가요? 화요일이나 목요일 오후가 제게는 가장 좋으며, \
# 약 45분 정도 소요될 예정입니다.

# 안녕히 계세요.
# 이순신
# '''
# }
## (note) 다음 문장을 생략하는 것이 작동을 더 잘 하는 것 같다.
##        비용을 절약할 수 있는 몇 가지 제안이 있습니다.
email_input_4 = {
    'from': '이순신 <yisunsin@client.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '세무 신고 시즌 통화 일정 잡기',
    'body': '''앤디님,

세금 신고 시즌이 다시 돌아왔습니다. \
올해 세금 계획 전략을 논의하기 위해 전화 상담을 예약하고 싶습니다. \
비용을 절약할 수 있는 몇 가지 제안이 있습니다.

다음 주에 시간이 있으신가요? 화요일이나 목요일 오후가 제게는 가장 좋으며, \
약 45분 정도 소요될 예정입니다. 캘린더 일정 확인하신 후 답변 부탁합니다.

안녕히 계세요.
이순신
'''
}
email_input_5 = {
    'from': '인사팀 <hr@a2i.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '알림: 경비 보고서 제출',
    'body': '''안녕하세요 앤디,

지난 달의 모든 경비 보고서를 이번 금요일까지 제출해야 한다는 친절한 알림입니다. \
모든 영수증과 적절한 문서를 포함해 주세요.

제출 과정에 대한 질문이 있으시면 언제든지 인사팀에 연락해 주세요.

좋은 하루 되세요.
인사팀
'''
}

email_input_6 = {
    'from': '권율 <yul.kwon@techpia.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '이 컨퍼런스에 참석하고 싶으신가요?',
    'body': '''안녕하세요 앤디님,

5월 15일-17일에 샌프란시스코에서 열리는 테크컨퍼런스 2025에 참가하시도록 초대하고자 연락드립니다.

이 컨퍼런스는 주요 기술 회사의 기조연설, AI와 ML 워크숍, 그리고 훌륭한 네트워킹 기회를 제공합니다. \
얼리버드 등록은 4월 30일까지 가능합니다.

참석에 관심이 있으신가요? 다른 팀원들도 참여를 원한다면 그룹 할인도 준비할 수 있습니다.

좋은 하루 되세요.
권율
'''
}

email_input_7 = {
    'from': '신사임당 <saimdang@partner.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '제출 전에 이 문서를 검토해 주실 수 있나요?',
    'body': '''앤디님,

헨더슨 프로젝트 제안서의 최종 버전을 첨부했습니다. 금요일에 클라이언트에게 제출하기 전에 \
기술 사양 섹션(15-20페이지)을 검토해 주실 수 있나요?

당신의 전문 지식이 필요한 모든 세부 사항을 다뤘는지 확인하는 데 정말 도움이 될 것입니다.

미리 감사드립니다.
신사임당
'''
}

email_input_8 = {
    'from': '시립 수영장 <info@cityrecreation.org>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '딸 수영 수업 등록',
    'body': '''앤디님께,

여름 수영 등록이 시작되었습니다! 작년에 딸분의 참여를 바탕으로, 중급 수준의 수업이 \
월요일과 수요일 오후 4시 또는 화요일과 목요일 오후 5시에 가능하다는 것을 알려드리고 싶었습니다.

수업은 6월 1일에 시작되어 8주 동안 진행됩니다. 자리가 제한되어 있으니 조기 등록을 권장합니다.

자리를 예약하고 싶으시면 알려주세요.

안녕히 계세요.
시립 레크리에이션 부서
'''
}

email_input_9 = {
    'from': 'GitHub <notifications@github.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': 'PR #42: alex-dev의 댓글',
    'body': '''안녕하세요!

alex-dev가 a2i/project의 풀 리퀘스트 #57에 댓글을 남겼습니다:.

> 변경 사항을 검토했는데 모든 것이 좋아 보입니다. auth_controller.py의 오류 처리에 대한 \
한 가지 작은 제안이 있습니다. 요청이 중단되는 것을 방지하기 위해 타임아웃 매개변수를 추가해야 할까요?

댓글 보기: https://github.com/a2i/project/pull/57#comment-12345

---
스레드를 작성했기 때문에 이 메시지를 받고 있습니다.
이 이메일에 직접 답장하거나 GitHub에서 확인하세요
'''
}

email_input_10 = {
    'from': '팀 리더 <teamlead@a2i.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '분기별 기획 회의',
    'body': '''안녕하세요 앤디,

분기별 기획 세션을 가질 시간입니다. 3분기 로드맵을 논의하기 위해 다음 주에 90분 회의를 예약하고 싶습니다.

월요일이나 수요일 중 언제 시간이 되는지 알려주실 수 있나요? 이상적으로는 오전 10시에서 오후 3시 사이가 좋겠습니다.

새로운 기능 우선순위에 대한 당신의 의견을 기대하고 있습니다.

좋은 하루 되세요.
팀 리더
'''
}

email_input_11 = {
    'from': 'AWS 모니터링 <no-reply@aws.amazon.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '시스템 관리자 경고: 인스턴스 CPU 사용률이 임계값 초과',
    'body': '''경고: 높은 CPU 사용률

다음 EC2 인스턴스가 15분 이상 CPU 사용률 임계값 90%를 초과했습니다.

인스턴스 ID: i-0b2d3e4f5a6b7c8d9
지역: us-west-2
현재 사용률: 95.3%

이 메시지는 자동으로 생성됩니다. 답장하지 마세요.
'''
}

email_input_12 = {
    'from': '고객 성공팀 <success@vendor.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '구독이 자동으로 갱신됩니다',
    'body': '''안녕하세요 앤디님,

개발자 프로 플랜의 연간 구독이 2025년 4월 15일에 자동으로 갱신된다는 친절한 알림입니다.

**** 4567로 끝나는 결제 방법으로 $1,499.00가 청구됩니다.

구독을 변경하고 싶으시면 갱신일 전에 계정 설정을 방문하거나 지원팀에 문의해 주세요.

지속적인 사업 관계에 감사드립니다!

고객 성공팀
'''
}

email_input_13 = {
    'from': '허준 <jun.heo@medical.org>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '연간 검진 알림',
    'body': '''안녕하세요 앤디님,

연간 건강 검진을 받을 시간이라는 알림입니다. 저희 기록에 따르면 마지막 방문이 약 1년 전이었습니다.

가능한 한 빨리 (02) 880-9385로 저희 사무실에 전화하여 약속을 잡아주세요.

좋은 하루 되세요.

허준 의원 사무실
'''
}

email_input_14 = {
    'from': '소셜 미디어 플랫폼 <notifications@social.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '5명이 당신의 게시물에 좋아요를 눌렀습니다',
    'body': '''안녕하세요 앤디님,

5명이 'NLP를 위한 머신러닝 기법'에 대한 최근 게시물에 좋아요를 눌렀습니다.

누가 게시물에 좋아요를 눌렀는지 확인하고 대화를 계속하세요!

[활동 보기]

이러한 알림을 구독 취소하려면 여기에서 설정을 조정하세요.
'''
}

email_input_15 = {
    'from': '프로젝트팀 <project@a2i.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '다음 달 공동 발표',
    'body': '''안녕하세요 앤디,

리더십팀에서 다음 달 전체 회의를 위해 최근 프로젝트 성공에 대한 공동 발표를 준비하라고 요청했습니다.

몇 가지 슬라이드를 만들기 시작했고 기술 아키텍처 섹션에 대한 당신의 의견을 주시면 감사하겠습니다. \
다음 주에 이에 대해 협력하기 위해 약 60분 정도 시간을 예약할 수 있을까요?

저는 일반적으로 화요일과 목요일에 시간이 됩니다.

감사합니다.
프로젝트팀
'''
}

email_input_16 = {
    'from': '마케팅팀 <marketing@openai.com>',
    'to': '온톨리지 <ontology@a2i.com>',
    'subject': '뉴스레터: OpenAI의 새로운 모델',
    'body': '''안녕하세요 앤디님,

OpenAI에서 새로운 모델을 출시했다는 것을 발표하게 되어 기쁩니다!

'GPT-5'라고 불리며 GPT-4의 후속작입니다.

지금 사용 가능하며 더 많은 정보는 [여기](https://openai.com/gpt-5)에서 찾을 수 있습니다.

감사합니다.
마케팅팀
'''
}

# --- 분류 결과: 'ignore'(무시), 'notify'(알림), 'respond'(응답) ------------------------
triage_output_1 = 'respond'
triage_output_2 = 'ignore'
triage_output_3 = 'notify'
triage_output_4 = 'respond'
triage_output_5 = 'notify'
triage_output_6 = 'respond'
triage_output_7 = 'respond'
triage_output_8 = 'respond'
triage_output_9 = 'notify'
triage_output_10 = 'respond'
triage_output_11 = 'notify'
triage_output_12 = 'notify'
triage_output_13 = 'respond'
triage_output_14 = 'ignore'
triage_output_15 = 'respond'
triage_output_16 = 'notify'

# --- 응답 기준 (해당되는 경우) -------------------------------------------------------------
response_criteria_1 = '''
- write_email 도구 호출로 질문을 확인하고 조사할 것임을 확약하는 이메일 발송하기  
'''  
# - Send email with write_email tool call to acknowledge the question and confirm it will be investigated  

response_criteria_2 = '''
- 응답 불필요
- 이런 내용은 무시하기
'''
# - No response needed
# - Ensure this is ignored  

response_criteria_3 = '''
- 응답 불필요
- 사용자에게 알림 처리하기
'''
# - No response needed
# - Ensure the user is notified  

response_criteria_4 = '''
- check_calendar_availability 도구 호출로 다음 주 화요일 또는 목요일 오후 일정 확인하기 
- 45분 회의 가능성 확인하기
- schedule_meeting 도구 호출로 캘린더 초대 발송하기 
- write_email 도구 호출로 세무 계획 요청을 확인하고 회의가 예약되었음을 알리는 이메일 발송하기  
'''
# - Check calendar availability for Tuesday or Thursday afternoon next week with check_calendar_availability tool call 
# - Confirm availability for a 45-minute meeting
# - Send calendar invite with schedule_meeting tool call 
# - Send email with write_email tool call to acknowledge tax planning request and notifying that a meeting has been scheduled  

response_criteria_5 = '''
- 응답 불필요
- 사용자에게 알림 처리하기
'''
# - No response needed
# - Ensure the user is notified  

response_criteria_6 = '''
- 테크컨퍼런스 2025 참석에 대한 관심을 표현하기
- AI/ML 워크숍에 대한 구체적인 질문하기
- 그룹 할인 세부 사항 문의하기
- write_email 도구 호출로 테크컨퍼런스 2025 참석에 대한 관심을 표현하고, AI/ML 워크숍에 대한 구체적인 질문을 하며, 그룹 할인 세부 사항을 문의하는 이메일 발송하기
'''
# - Express interest in attending TechConf 2025
# - Ask specific questions about AI/ML workshops
# - Inquire about group discount details
# - Send email with write_email tool call to express interest in attending TechConf 2025, ask specific questions about AI/ML workshops, and inquire about group discount details

response_criteria_7 = '''
- 기술 사양 검토에 명시적으로 동의하기
- 금요일 마감일 확인하기
- write_email 도구 호출로 기술 사양 검토에 명시적으로 동의하고 금요일 마감일을 확인하는 이메일 발송하기
'''
# - Explicitly agree to review the technical specifications
# - Acknowledge Friday deadline
# - Send email with write_email tool call to explicitly agree to review the technical specifications and acknowledge Friday deadline

response_criteria_8 = '''
- write_email 도구 호출로 딸의 수영 수업 등록에 관심을 표현하는 이메일 발송하기
'''
# - Send email with write_email tool call to express interest in registering daughter for swimming class

response_criteria_9 = '''
- 응답 불필요
- 사용자에게 알림 처리하기
'''
# - No response needed
# - Ensure the user is notified  

response_criteria_10 = '''
- check_calendar_availability 도구 호출로 월요일 또는 수요일 90분 회의 가능성 확인하기
- write_email 도구 호출로 요청을 확인하고 가능한 시간을 제공하는 이메일 발송하기  
'''
# - Check calendar for 90-minute meeting availability for Monday or Wednesday with check_calendar_availability tool call 
# - Send email acknowledging the request and providing availability with write_email tool call  

response_criteria_11 = '''
- 응답 불필요
- 사용자에게 알림 처리하기
'''
# - No response needed
# - Ensure the user is notified  

response_criteria_12 = '''
- 응답 불필요
- 사용자에게 알림 처리하기
'''
# - No response needed
# - Ensure the user is notified  

response_criteria_13 = '''
- 연간 건강 검진 알림 확인하기
- write_email 도구 호출로 연간 건강 검진 알림을 확인하는 이메일 발송하기
'''
# - Acknowledge annual checkup reminder
# - Send email with write_email tool call to acknowledge annual checkup reminder

response_criteria_14 = '''
- 응답 불필요
- 이것이 무시되도록 확인  
'''
# - No response needed
# - Ensure this is ignored  

response_criteria_15 = '''
- check_calendar_availability 도구 호출로 화요일 또는 목요일 60분 회의 가능성 확인하기
- schedule_meeting 도구 호출로 캘린더 초대 발송하기
- write_email 도구 호출로 공동 발표 협력에 동의하고 회의가 예약되었음을 알리는 이메일 발송하기
'''
# - Check calendar for 60-minute meeting availability for Tuesday or Thursday with check_calendar_availability tool call 
# - Send calendar invite with schedule_meeting tool call 
# - Send email with write_email tool call to agree to joint presentation and notify that a meeting has been scheduled

response_criteria_16 = '''
- 응답 불필요
- 사용자에게 알림 처리하기
'''
# - No response needed
# - Ensure the user is notified  

examples_triage = [
  {
    'inputs': {'email_input': email_input_1},
    'outputs': {'classification': triage_output_1},
  },
  {
    'inputs': {'email_input': email_input_2},
    'outputs': {'classification': triage_output_2},
  },
  {
    'inputs': {'email_input': email_input_3},
    'outputs': {'classification': triage_output_3},
  },
  {
    'inputs': {'email_input': email_input_4},
    'outputs': {'classification': triage_output_4},
  },
  {
    'inputs': {'email_input': email_input_5},
    'outputs': {'classification': triage_output_5},
  },
  {
    'inputs': {'email_input': email_input_6},
    'outputs': {'classification': triage_output_6},
  },
  {
    'inputs': {'email_input': email_input_7},
    'outputs': {'classification': triage_output_7},
  },
  {
    'inputs': {'email_input': email_input_8},
    'outputs': {'classification': triage_output_8},
  },
  {
    'inputs': {'email_input': email_input_9},
    'outputs': {'classification': triage_output_9},
  },
  {
    'inputs': {'email_input': email_input_10},
    'outputs': {'classification': triage_output_10},
  },
  {
    'inputs': {'email_input': email_input_11},
    'outputs': {'classification': triage_output_11},
  },
  {
    'inputs': {'email_input': email_input_12},
    'outputs': {'classification': triage_output_12},
  },
  {
    'inputs': {'email_input': email_input_13},
    'outputs': {'classification': triage_output_13},
  },
  {
    'inputs': {'email_input': email_input_14},
    'outputs': {'classification': triage_output_14},
  },
  {
    'inputs': {'email_input': email_input_15},
    'outputs': {'classification': triage_output_15},
  },
  {
    'inputs': {'email_input': email_input_16},
    'outputs': {'classification': triage_output_16},
  },
]

email_inputs = [
    email_input_1, email_input_2, email_input_3, email_input_4, email_input_5,
    email_input_6, email_input_7, email_input_8, email_input_9, email_input_10,
    email_input_11, email_input_12, email_input_13, email_input_14, email_input_15,
    email_input_16
]

email_names = [
    'email_input_1', 'email_input_2', 'email_input_3', 'email_input_4', 'email_input_5',
    'email_input_6', 'email_input_7', 'email_input_8', 'email_input_9', 'email_input_10',
    'email_input_11', 'email_input_12', 'email_input_13', 'email_input_14', 'email_input_15',
    'email_input_16'
]

response_criteria_list = [
    response_criteria_1, response_criteria_2, response_criteria_3, response_criteria_4, response_criteria_5,
    response_criteria_6, response_criteria_7, response_criteria_8, response_criteria_9, response_criteria_10,
    response_criteria_11, response_criteria_12, response_criteria_13, response_criteria_14, response_criteria_15,
    response_criteria_16
]

triage_outputs_list = [
    triage_output_1, triage_output_2, triage_output_3, triage_output_4, triage_output_5,
    triage_output_6, triage_output_7, triage_output_8, triage_output_9, triage_output_10,
    triage_output_11, triage_output_12, triage_output_13, triage_output_14, triage_output_15,
    triage_output_16
]

# 내용 분석에 따른 각 이메일 응답에 대한 예상 도구 호출 정의
# 옵션: write_email, schedule_meeting, check_calendar_availability, DoneSchema
expected_tool_calls = [
    ['write_email', 'DoneSchema'],                                                     # email_input_1: API 문서 질문
    [],                                                                                # email_input_2: 뉴스레터 알림 - 무시
    [],                                                                                # email_input_3: 시스템 유지보수 알림 - 알림만
    ['check_calendar_availability', 'schedule_meeting', 'write_email', 'DoneSchema'],  # email_input_4: 세무 통화 일정
    [],                                                                                # email_input_5: 경비 보고서 알림 - 알림만
    ['write_email', 'DoneSchema'],                                                     # email_input_6: 컨퍼런스 초대 - 응답 필요
    ['write_email', 'DoneSchema'],                                                     # email_input_7: 문서 검토 요청
    ['write_email', 'DoneSchema'],                                                     # email_input_8: 수영 수업 등록
    [],                                                                                # email_input_9: GitHub PR 댓글 - 알림만
    ['check_calendar_availability', 'write_email', 'DoneSchema'],                      # email_input_10: 기획 회의
    [],                                                                                # email_input_11: AWS 경고 - 알림만
    [],                                                                                # email_input_12: 구독 갱신 - 무시
    ['write_email', 'DoneSchema'],                                                     # email_input_13: 의사 예약 알림
    [],                                                                                # email_input_14: 소셜 미디어 알림 - 조치 불필요
    ['check_calendar_availability', 'schedule_meeting', 'write_email', 'DoneSchema'],  # email_input_15: 공동 발표
    [],                                                                                # email_input_16: 뉴스레터 - 알림만
]