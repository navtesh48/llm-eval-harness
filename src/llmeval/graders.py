"""Grader registry. Adding a grader is one decorated function."""
import re, json
from dataclasses import dataclass
from llmeval.suite import GraderSpec

@dataclass
class Grade:
    passed: bool
    detail: str = ''

REG = {}
def grader(name):
    def deco(f): REG[name] = f; return f
    return deco

@grader('contains')
def _contains(out, s, ctx):
    miss = [v for v in s['values'] if v.lower() not in out.lower()]
    return Grade(not miss, f'missing {miss}' if miss else '')

@grader('contains_any')
def _any(out, s, ctx):
    ok = any(v.lower() in out.lower() for v in s['values'])
    return Grade(ok, '' if ok else f"none of {s['values']} found")

@grader('not_contains')
def _not(out, s, ctx):
    bad = [v for v in s['values'] if v.lower() in out.lower()]
    return Grade(not bad, f'found forbidden {bad}' if bad else '')

@grader('regex')
def _regex(out, s, ctx):
    ok = re.search(s['pattern'], out, flags=re.I | re.S) is not None
    return Grade(ok, '' if ok else f"pattern {s['pattern']} not matched")

@grader('json_valid')
def _json(out, s, ctx):
    try:
        j = json.loads(out)
    except Exception as e:
        return Grade(False, f'invalid JSON: {e}')
    miss = [k for k in s.get('keys', []) if not isinstance(j, dict) or k not in j]
    return Grade(not miss, f'missing keys {miss}' if miss else '')

@grader('max_chars')
def _max(out, s, ctx):
    return Grade(len(out) <= s['value'], f'{len(out)} chars')

@grader('latency_ms_max')
def _lat(out, s, ctx):
    return Grade(ctx['latency_ms'] <= s['value'], f"{ctx['latency_ms']:.0f} ms")

@grader('llm_rubric')
def _rubric(out, s, ctx):
    from llmeval.judge import judge
    v = judge(ctx['input'], out, s['rubric'], ctx.get('use_cache', True))
    return Grade(v.passed, v.reason)

def grade(out: str, spec: GraderSpec, ctx: dict) -> Grade:
    if spec.type not in REG: raise KeyError(f'unknown grader {spec.type}; known: {sorted(REG)}')
    return REG[spec.type](out, spec.model_dump(), ctx)
