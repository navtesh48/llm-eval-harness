from llmeval.compare import compare

def run(passes): return {'results': [{'case_id': k, 'passed': v} for k, v in passes.items()]}

def test_regression_detected():
    r = compare(run({'a': True, 'b': True}), run({'a': True, 'b': False}))
    assert r['regressions'] == ['b'] and r['failed']

def test_no_regression_ok():
    assert not compare(run({'a': True}), run({'a': True}))['failed']

def test_improvement_and_new_cases_reported_not_failed():
    r = compare(run({'a': False}), run({'a': True, 'z': True}))
    assert r['improvements'] == ['a'] and r['new_cases'] == ['z'] and not r['failed']
