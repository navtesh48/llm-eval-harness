import pytest
from llmeval.suite import GraderSpec
from llmeval.graders import grade

def g(**kw): return GraderSpec(**kw)

def test_contains_and_not():
    assert grade('Hello World', g(type='contains', values=['hello']), {}).passed
    assert not grade('Hello', g(type='not_contains', values=['hell']), {}).passed
    assert grade('abc', g(type='contains_any', values=['x', 'b']), {}).passed

def test_json_keys():
    assert grade('{"a":1}', g(type='json_valid', keys=['a']), {}).passed
    assert not grade('{"a":1}', g(type='json_valid', keys=['b']), {}).passed
    assert not grade('nope', g(type='json_valid'), {}).passed

def test_regex_and_max_chars():
    assert grade('pH 7.5', g(type='regex', pattern=r'ph\s*7\.\d'), {}).passed
    assert not grade('toolong', g(type='max_chars', value=3), {}).passed

def test_latency():
    assert grade('', g(type='latency_ms_max', value=100), {'latency_ms': 50}).passed

def test_unknown_grader_is_a_clear_error():
    with pytest.raises(KeyError, match='unknown grader'):
        grade('x', g(type='nope'), {})
