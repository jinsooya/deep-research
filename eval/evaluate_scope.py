import uuid
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langsmith import Client
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv('/Users/jinsoopark/Dropbox/_data/projects/python/ai/deep_research/.env')

from prompts import BRIEF_CRITERIA, BRIEF_HALLUCINATION
from src.deep_research_multi_agent.research_agent_scope import scope_research_workflow

# --- Pydantic Data Schemas ---------------------------------------------------
class Criteria(BaseModel):
    """
    개별 성공 기준 평가 결과

    리서치 브리프에 포함되어야 하는 단일 기준과, 해당 기준이 충족되었는지 여부 및 근거를 기술한다.
    
    Individual success criteria evaluation result.
    
    This model represents a single evaluation criteria that should be present
    in the research brief, along with a detailed assessment of whether it was
    successfully captured and the reasoning behind that assessment.
    """
    criteria_text: str = Field(
        # description="평가 대상 성공 기준 텍스트(예: '현재 나이 25세', '월세 7천 달러 미만')"
        description="The specific success criteria being evaluated (e.g., 'Current age is 25', 'Monthly rent below 7k')"
    )
    reasoning: str = Field(
        # description='해당 기준이 충족되었는지 여부를 판단한 근거를 구체적으로 설명한다. 브리프의 관련 증거를 포함한다.'
        description="Detailed explanation of why this criteria is or isn't captured in the research brief, including specific evidence from the brief"
    )
    is_captured: bool = Field(
        # description='리서치 브리프가 해당 기준을 충분히 반영했는지 여부를 나타낸다(True/False)'
        description='Whether this specific criteria is adequately captured in the research brief (True) or missing/inadequately addressed (False)'
    )

class NoAssumptions(BaseModel):
    """
    불필요한 가정 여부 평가 모델

    이 모델은 리서치 브리프가 사용자 대화에서 명시되지 않은 가정이나 추론,
    추가 정보를 포함하는지를 평가한다. 또한 평가 판단에 대한 상세 근거를 제공한다.
    
    Evaluation model for checking if research brief makes unwarranted assumptions.
    
    This model evaluates whether the research brief contains any assumptions,
    inferences, or additions that were not explicitly stated by the user in their
    original conversation. It provides detailed reasoning for the evaluation decision.
    """
    no_assumptions: bool = Field(
        # description='리서치 브리프가 불필요한 가정을 피했는지 여부. 사용자가 명시적으로 제공한 정보만 포함하면 True, 명시되지 않은 가정을 추가하면 False'
        description='Whether the research brief avoids making unwarranted assumptions. True if the brief only includes information explicitly provided by the user, False if it makes assumptions beyond what was stated.'
    )
    reasoning: str = Field(
        # description='평가 판단의 상세 근거. 발견된 가정의 구체적 예시 또는 가정이 전혀 없다는 확인 내용을 포함한다.'
        description="Detailed explanation of the evaluation decision, including specific examples of any assumptions found or confirmation that no assumptions were made beyond the user's explicit statements."
    )

# --- Evaluation Functions ----------------------------------------------------
def evaluate_success_criteria(outputs: dict, reference_outputs: dict):
    """
    리서치 브리프가 요구한 성공 기준을 충족하는지 평가한다.

    각 기준을 개별적으로 평가하여 충족 여부와 근거를 반환한다.

    Evaluate whether the research brief captures all required success criteria.
    
    This function evaluates each criterion individually to provide focused assessment
    and detailed reasoning for each evaluation decision.

    Args:
        outputs: 평가 대상 연구 브리프를 담은 딕셔너리. 키는 'research_brief'여야 한다.
        outputs: Dictionary containing the research brief to evaluate
        reference_outputs: 성공 기준 목록을 담은 딕셔너리. 키는 'criteria'여야 한다.
        reference_outputs: Dictionary containing the list of success criteria

    Returns:
        dict[str, Any]: 전체 점수(0.0~1.0)와 개별 기준 평가 상세를 담은 딕셔너리.
        Dict with evaluation results including score (0.0 to 1.0)
    """
    research_brief = outputs['research_brief']
    success_criteria = reference_outputs['criteria']

    # LLM 초기화
    model = init_chat_model(model='openai:gpt-5')  
    # model = init_chat_model(model='anthropic:claude-sonnet-4-5') 
    structured_output_model = model.with_structured_output(Criteria)
    
    # 기준별 평가 실행 run evals
    responses = structured_output_model.batch([
        [HumanMessage(content=BRIEF_CRITERIA.format(
            research_brief=research_brief,
            criterion=criterion
        ))] 
        for criterion in success_criteria
    ])

    # 개별 평가 결과 구성
    # ensure the criteria_text field is populated correctly
    individual_evaluations = [
        Criteria(
            reasoning=response.reasoning,
            criteria_text=criterion,
            is_captured=response.is_captured
        )
        for criterion, response in zip(success_criteria, responses)
    ]

    # 전체 점수 계산
    # calculate overall score as percentage of captured criteria
    captured_count = sum(
        1 for eval_result in individual_evaluations if eval_result.is_captured
    )
    total_count = len(individual_evaluations)
    
    return {
        'key': 'success_criteria_score', 
        'score': captured_count / total_count if total_count > 0 else 0.0,
        'individual_evaluations': [
            {
                'criteria': eval_result.criteria_text,
                'captured': eval_result.is_captured,
                'reasoning': eval_result.reasoning
            }
            for eval_result in individual_evaluations
        ]
    }


def evaluate_no_assumptions(outputs: dict, reference_outputs: dict):
    """
    리서치 브리프가 불필요한 가정을 포함하지 않았는지 평가한다.

    이 함수는 브리프가 사용자 대화에서 명시적으로 제공된 정보와 요구사항만을 반영했는지,
    혹은 명시되지 않은 선호나 조건을 가정하여 추가했는지를 확인한다.

        
    Evaluate whether the research brief avoids making unwarranted assumptions.
    
    This evaluator checks that the research brief only includes information
    and requirements that were explicitly provided by the user, without
    making assumptions about unstated preferences or requirements.

    Args:
        outputs: 평가할 리서치 브리프를 담은 딕셔너리. 키는 'research_brief'여야 한다.
        outputs: Dictionary containing the research brief to evaluate
        reference_outputs: 비교 기준으로 사용할 성공 기준을 담은 딕셔너리. 키는 'criteria'여야 한다.
        reference_outputs: Dictionary containing the success criteria for reference

    Returns:
        dict: 평가 결과. 불필요한 가정 회피 여부(boolean 점수)와 상세 근거(reasoning)를 포함한다.
        Dict with evaluation results including boolean score and detailed reasoning
    """
    research_brief = outputs['research_brief']
    success_criteria = reference_outputs['criteria']
    
    # model = init_chat_model(model='openai:gpt-5')  
    model = init_chat_model(model='anthropic:claude-sonnet-4-5')  
    structured_output_model = model.with_structured_output(NoAssumptions)
    
    response = structured_output_model.invoke([
        HumanMessage(content=BRIEF_HALLUCINATION.format(
            research_brief=research_brief, 
            success_criteria=str(success_criteria)
        ))
    ])
    
    return {
        'key': 'no_assumptions_score', 
        'score': response.no_assumptions,
        'reasoning': response.reasoning
    }

def target_func(inputs: dict):
    config = {'configurable': {'thread_id': uuid.uuid4()}}
    return scope_research_workflow.invoke(inputs, config=config)

if __name__ == '__main__':
    client = Client()
    dataset_name = 'Deep Research Scoping'
    client.evaluate(
        target_func,
        data=dataset_name,
        evaluators=[evaluate_success_criteria, evaluate_no_assumptions],
        experiment_prefix='Deep Research Scoping'
    )
    print(f'*** Evaluation complete! *******')


# --- How to Run ----------------------------------------------------------------
# 1. 프로젝트 루트로 이동
# % cd /Users/jinsoopark/Dropbox/_data/projects/python/ai/deep_research

# 2. 평가 스크립트 실행
# % PYTHONPATH=/Users/jinsoopark/Dropbox/_data/projects/python/ai/deep_research python eval/evaluate_scope.pPYTHONPATH=/Users/jinsoopark/Dropbox/_data/projects/python/ai/deep_research python eval/evaluate_scope.pyy