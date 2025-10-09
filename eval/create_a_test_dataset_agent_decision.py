from langsmith import Client
from dotenv import load_dotenv

import deep_research_agent_decision_test_dataset

load_dotenv()


# LangSmith 클라이언트를 초기화한다.
# initialize the LangSmith client
client = Client()

# 데이터셋 이름을 정의한다.
dataset_name = 'Deep Research Agent Termination Decision'

# 데이터셋 상태 확인
print(f'> 데이터셋 확인 중: {dataset_name}')


if not client.has_dataset(dataset_name=dataset_name):
    # 데이터셋을 생성한다
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description='A dataset that evaluates whether a researcher can accurately decide to continue calling tools, or to stop.'
    )
    
    # 데이터셋에 예시를 추가한다.
    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                'inputs': {'researcher_messages': deep_research_agent_decision_test_dataset.messages_should_continue},
                'outputs': {'next_step': 'continue'}
            },
            {
                'inputs': {'researcher_messages': deep_research_agent_decision_test_dataset.messages_should_stop},
                'outputs': {'next_step': 'stop'}
            }
        ]
    )
else:
    print(f"> 데이터셋 '{dataset_name}'이 이미 존재합니다.")