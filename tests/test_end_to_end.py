"""Proves the harness catches a regression: good prompt -> baseline; bad prompt -> exit 1; revert -> exit 0."""
import json, os, pytest
from llmeval import cache, cli
from llmeval.runner import run_suite
from llmeval.suite import load_suite
import fakeapp

SUITE = """
name: fake
target: {type: python, callable: 'fakeapp:answer'}
cases:
  - {id: ph, input: 'ph?', graders: [{type: contains, values: ['pH 7']}]}
  - {id: temp, input: 'temp?', graders: [{type: regex, pattern: '\\b28\\b'}, {type: max_chars, value: 100}]}
"""

@pytest.fixture
def suite_file(tmp_path, monkeypatch):
    p = tmp_path / 'suite.yml'; p.write_text(SUITE)
    monkeypatch.chdir(tmp_path); monkeypatch.delenv('FAKE_MODE', raising=False); cache.clear()
    return str(p)

def run_cli(monkeypatch, *argv):
    monkeypatch.setattr('sys.argv', ['llmeval', *argv])
    try:
        cli.main(); return 0
    except SystemExit as e:
        return e.code

def test_regression_is_caught_then_cleared(suite_file, monkeypatch):
    assert run_cli(monkeypatch, 'run', suite_file, '--repeats', '2', '--no-cache', '--save-as-baseline', 'baseline.json') == 0
    base = json.load(open('baseline.json'))
    assert all(r['passed'] for r in base['results']) and len(base['results']) == 4

    monkeypatch.setenv('FAKE_MODE', 'bad')                      # break the app on purpose
    assert run_cli(monkeypatch, 'run', suite_file, '--repeats', '2', '--no-cache', '--baseline', 'baseline.json') == 1

    monkeypatch.delenv('FAKE_MODE')                              # revert
    assert run_cli(monkeypatch, 'run', suite_file, '--repeats', '2', '--no-cache', '--baseline', 'baseline.json') == 0

def test_second_run_makes_zero_target_calls_and_no_cache_forces_fresh(suite_file):
    suite = load_suite(suite_file)
    fakeapp.CALLS['n'] = 0
    run_suite(suite, repeats=2); first = fakeapp.CALLS['n']
    run_suite(suite, repeats=2); assert fakeapp.CALLS['n'] == first          # all cached
    run_suite(suite, repeats=2, use_cache=False); assert fakeapp.CALLS['n'] == first * 2

def test_report_shows_wilson_interval(suite_file):
    run = run_suite(load_suite(suite_file), use_cache=False)
    from llmeval.report import to_html
    assert '95% interval' in to_html(run)

def test_target_errors_are_recorded_not_raised(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path); cache.clear()
    p = tmp_path / 's.yml'
    p.write_text("name: x\ntarget: {type: python, callable: 'fakeapp:missing'}\ncases:\n  - {id: a, input: hi, graders: [{type: contains, values: ['x']}]}\n")
    run = run_suite(load_suite(str(p)), use_cache=False)
    assert run['results'][0]['passed'] is False and 'error' in run['results'][0]
