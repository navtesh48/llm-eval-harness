from pydantic import BaseModel
from llmeval.llm import structured
from llmeval.cache import key, cached

class Verdict(BaseModel):
    reason: str        # write the reason BEFORE the verdict so the model reasons first
    passed: bool

SYSTEM = ('You are a strict grader. You get a question, an AI answer, and a rubric. Check each rubric statement against '
          'the answer only. Do not reward length or confidence. If any rubric statement is not clearly satisfied, fail it. '
          'Give a one or two sentence reason first, then the verdict.')

def judge(question: str, answer: str, rubric: str, use_cache: bool = True) -> Verdict:
    user = f'Question:\n{question}\n\nAnswer:\n{answer}\n\nRubric:\n{rubric}'
    d = cached(key('judge', user), lambda: structured(Verdict, SYSTEM, user, max_tokens=400).model_dump(), use_cache)
    return Verdict(**d)
