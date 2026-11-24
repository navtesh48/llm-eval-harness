import yaml
from pydantic import BaseModel, ConfigDict
from typing import Literal

class GraderSpec(BaseModel):
    model_config = ConfigDict(extra='allow')    # grader-specific keys such as values, pattern, rubric
    type: str

class Case(BaseModel):
    id: str
    input: str
    graders: list[GraderSpec]
    tags: list[str] = []

class Target(BaseModel):
    type: Literal['http', 'python', 'anthropic']
    url: str | None = None
    body: dict | None = None
    output_path: str | None = None
    callable: str | None = None            # 'package.module:function', takes str returns str
    system: str | None = None
    model: str | None = None
    max_tokens: int = 500

class Suite(BaseModel):
    name: str
    target: Target
    cases: list[Case]

def load_suite(path: str) -> Suite:
    s = Suite(**yaml.safe_load(open(path)))
    ids = [c.id for c in s.cases]
    assert len(ids) == len(set(ids)), 'duplicate case ids'
    return s
