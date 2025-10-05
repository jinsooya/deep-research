"""
LangSmith 데이터셋을 준비하고 전자메일 분류 에이전트를 평가하며, 평가 결과를 시각화하여 파일로 저장한다.
- 데이터셋이 없으면 생성하고 예시를 추가한다.
- 워크플로 에이전트를 대상으로 등록하여 모델 출력이 기준 정답과
  대소문자를 무시하고 완전히 동일한지 확인하는 방식으로 평가한다.
- 평균 점수를 막대 그래프로 저장한다.
"""

from .email_test_dataset import examples_triage
from ..src.email_agent.email_agent import my_email_agent

from langsmith import Client
# from langsmith import testing as t  # 사용 여부가 향후 추가될 수 있어 유지한다.  # noqa: F401

from typing import Any
from pathlib import Path
from datetime import datetime
from matplotlib import pyplot


# --- Client ----------------------------------------------------------------
# langsmith.Client 객체를 생성한다.
client = Client()

# --- Dataset ----------------------------------------------------------------
# 데이터셋 이름을 정의한다. 기존 이름을 유지하여 LangSmith 내 식별 일관성을 보장한다.
dataset_name = 'LangChain Academy: E-mail Triage Dataset'

# 데이터셋 존재 여부를 확인하고 없으면 생성한다.
if not client.has_dataset(dataset_name=dataset_name):
    # 데이터셋을 생성한다.
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        # description='전자메일과 분류 결정을 포함한 데이터셋'
        description="A dataset of e-mails and their triage decisions."
    )
    # 예시를 데이터셋에 추가한다.
    client.create_examples(dataset_id=dataset.id, examples=examples_triage)


# --- Target functions that run our email agents ------------------------------
def target_email_agent(inputs: dict[str, Any]) -> dict[str, str]:
    """
    Process an email through the workflow-based email assistant.
    전자메일 입력을 워크플로 기반 이메일 어시스턴트로 처리한다.

    Parameters
    ----------
    inputs : dict[str, Any]
        데이터셋에서 제공하는 'email' 키를 포함한 입력 딕셔너리

    Returns
    -------
    dict[str, str]
        에이전트의 분류 결과를 'classification_decision' 키로 반환한다.
        오류 또는 누락 시 'unknown'을 반환한다.
    """
    try:
        # 워크플로 에이전트를 호출하여 분류 결과를 획득한다.
        response = my_email_agent.invoke({'email': inputs['email']})
        # 예상 키가 존재하면 해당 값을 반환한다.
        if 'classification_decision' in response:
            return {'classification_decision': response['classification_decision']}
        # 키가 없을 때는 알리고 unknown으로 대체한다.
        print('워크플로 에이전트 응답에 classification_decision 키가 없습니다.')
        # print("No 'classification_decision' in response from workflow agent")
        return {'classification_decision': 'unknown'}
    except Exception as e:  # 예외 발생 시 알리고 unknown으로 대체한다.
        print(f'워크플로 에이전트 처리 중 오류가 발생했습니다: {e}')
        # print(f'Error in workflow agent: {e}')
        return {'classification_decision': 'unknown'}


# --- Evaluator ----------------------------------------------------------------
# LangSmith에 저장할 피드백 키를 정의한다.
feedback_key = 'classification'


def classification_evaluator(outputs: dict[str, str], reference_outputs: dict[str, str]) -> bool:
    """
    Check if the answer exactly matches the expected answer.
    모델 출력이 기준 정답과 대소문자를 무시하고 완전히 동일한지 확인한다.

    Parameters
    ----------
    outputs : dict[str, str]
        대상 함수가 반환한 출력으로 'classification_decision' 키를 포함한다.
    reference_outputs : dict[str, str]
        데이터셋의 기준 정답으로 'classification' 키를 포함한다.

    Returns
    -------
    bool
        두 문자열이 대소문자를 무시했을 때 완전히 동일하면 True, 아니면 False이다.
    """
    # 대소문자를 무시하고 정확 일치를 평가한다.
    return outputs['classification_decision'].lower() == reference_outputs['classification'].lower()


# 평가를 실행한다.
experiment_results_workflow = client.evaluate(
    target_email_agent,                             # 대상 에이전트 함수를 설정한다.
    data=dataset_name,                              # 사용할 데이터셋을 지정한다.
    evaluators=[classification_evaluator],          # 평가지정자 리스트를 설정한다.
    experiment_prefix='E-mail assistant workflow',  # 실험 이름 접두어를 지정한다.
    max_concurrency=2                               # 동시 실행 개수를 제한한다.
        ## The maximum number of concurrent evaluations to run. 
        ## > If None then no limit is set. 
        ## > If 0 then no concurrency. 
        ## > Defaults to 0.
)

# --- Visualization ------------------------------------------------------------
# 평가 결과를 데이터프레임으로 변환한다.
df = experiment_results_workflow.to_pandas()

# 평균 점수를 계산한다. 해당 컬럼이 없으면 0.0으로 처리한다.
workflow_score = (
    df['feedback.classification_evaluator'].mean()
        if 'feedback.classification_evaluator' in df.columns
        else 0.0
)

# 막대 그래프를 생성한다.
pyplot.figure(figsize=(10, 6))
models = ['Agentic Workflow']  # 모델 이름 리스트
scores = [workflow_score]      # 점수 리스트

# 막대 그래프를 그린다.
pyplot.bar(models, scores, width=0.5)

# 레이블과 제목을 설정한다.
pyplot.xlabel('Agent Type')
pyplot.ylabel('Average Score')
pyplot.title(f'Email Triage Performance Comparison - {feedback_key.capitalize()} Score')

# 각 막대 위에 점수를 표기한다.
for i, score in enumerate(scores):
    pyplot.text(i, score + 0.02, f'{score:.2f}', ha='center', fontweight='bold')

# y축 범위를 설정한다.
pyplot.ylim(0, 1.1)

# 가독성을 위해 격자를 추가한다.
pyplot.grid(axis='y', linestyle='--', alpha=0.7)

# 출력 디렉토리를 보장한다. pathlib을 사용한다.
out_dir = Path('results/triage')
out_dir.mkdir(parents=True, exist_ok=True)

# 타임스탬프를 사용하여 파일명을 생성한다.
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
plot_path = out_dir / f'triage_comparison_{timestamp}.png'

# 그래프를 저장하고 자원을 정리한다.
pyplot.savefig(plot_path)
pyplot.close()

print(f'\n평가 그래프가 다음 위치에 저장되었습니다: {plot_path}')
print(f'Agent With Router 점수: {workflow_score:.2f}')