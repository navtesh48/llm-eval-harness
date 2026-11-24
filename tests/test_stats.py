from llmeval.stats import wilson, kappa

def test_wilson_known_value():
    lo, hi = wilson(40, 50)
    assert 0.66 < lo < 0.68 and 0.88 < hi < 0.90

def test_wilson_empty():
    assert wilson(0, 0) == (0.0, 1.0)

def test_kappa():
    assert kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert kappa([True, True, False, False], [False, False, True, True]) == -1.0
