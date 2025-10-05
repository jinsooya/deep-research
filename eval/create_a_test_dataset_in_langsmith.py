import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from langsmith import Client
from src.eval.email_test_dataset import examples_triage

from dotenv import load_dotenv

load_dotenv('.env')


# LangSmith 클라이언트를 초기화한다.
client = Client()

# 데이터셋 이름을 정의한다.
dataset_name = 'E-mail Agent Triage Test Dataset'

# 데이터셋 상태 확인
print(f'> 데이터셋 확인 중: {dataset_name}')

try:
    # 데이터셋이 존재하는지 확인
    dataset_exists = client.has_dataset(dataset_name=dataset_name)
    print(f'> 데이터셋 존재 여부: {dataset_exists}')
    
    if not dataset_exists:
        print('새 데이터셋 생성 중...')
        dataset = client.create_dataset(
            dataset_name=dataset_name, 
            description='이메일과 분류(트리아지) 결과를 담은 데이터셋이다.'
        )
        print(f'> 데이터셋 생성 완료! ID: {dataset.id}')
        
        print(f'> 예시 추가 중... (총 {len(examples_triage)}개)')
        client.create_examples(dataset_id=dataset.id, examples=examples_triage)
        print('> 예시 추가 완료!')
        
    else:
        print('>  데이터셋이 이미 존재합니다.')
        
        # 기존 데이터셋 정보 확인
        existing_dataset = client.read_dataset(dataset_name=dataset_name)
        print(f'> 기존 데이터셋 ID: {existing_dataset.id}')
        print(f'> 기존 데이터셋 설명: {existing_dataset.description}')
        
except Exception as e:
    print(f'오류 발생: {e}')
    print(f'오류 타입: {type(e).__name__}')