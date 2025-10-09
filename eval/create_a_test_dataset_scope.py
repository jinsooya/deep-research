from langsmith import Client
from dotenv import load_dotenv

import deep_research_scope_test_dataset

# load_dotenv('.env')
load_dotenv('/Users/jinsoopark/Dropbox/_data/projects/python/ai/deep_research/.env')


# LangSmith 클라이언트를 초기화한다.
# initialize the LangSmith client
client = Client()

# 데이터셋 이름을 정의한다.
dataset_name = 'Deep Research Scoping'

# 데이터셋 상태 확인
print(f'> 데이터셋 확인 중: {dataset_name}')


if not client.has_dataset(dataset_name=dataset_name):
    # 데이터셋을 생성한다
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description='A dataset that measures the quality of research briefs generated from an input conversation'
    )
    
    # 데이터셋에 예시를 추가한다.
    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {   
                'inputs': {'messages': deep_research_scope_test_dataset.conversation_1},
                'outputs': {'criteria': deep_research_scope_test_dataset.criteria_1}
            },
            {
                'inputs': {'messages': deep_research_scope_test_dataset.conversation_2},
                'outputs': {'criteria': deep_research_scope_test_dataset.criteria_2}
            },
            {
                'inputs': {'messages': deep_research_scope_test_dataset.conversation_3},
                'outputs': {'criteria': deep_research_scope_test_dataset.criteria_3}
            }
        ]
    )
else:
    print(f"> 데이터셋 '{dataset_name}'이 이미 존재합니다.")