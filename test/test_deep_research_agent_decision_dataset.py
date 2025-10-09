import uuid
from langsmith import Client
from dotenv import load_dotenv#, find_dotenv

from deep_research_multi_agent.research_agent import researcher_workflow 

load_dotenv()

# LangSmith 클라이언트를 초기화한다.
client = Client()

# 데이터셋 이름을 정의한다.
dataset_name = 'Deep Research Agent Termination Decision'

def evaluate_next_step(outputs: dict, reference_outputs:dict):
    tool_calls = outputs['researcher_messages'][-1].tool_calls
    made_tool_call = len(tool_calls) > 0
    return {
        'key': 'correct_next_step',
        'score': made_tool_call == (reference_outputs['next_step'] == 'continue')
    }

def target_func(inputs: dict):
    config = {'configurable': {'thread_id': uuid.uuid4()}}
    result = researcher_workflow.nodes['Research Agent'].invoke(inputs, config=config)
    return result

client.evaluate(
    target_func,
    data=dataset_name,
    evaluators=[evaluate_next_step],
    experiment_prefix='Researcher Iteration',
)