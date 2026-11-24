# llmeval: Regression Harness for LLM Apps

A command-line tool that runs a test suite against any LLM app on every commit and tells you whether quality dropped. Describe cases in YAML, point it at an HTTP endpoint, a Python function or a bare prompt, and it runs every case, grades the outputs, caches results, writes an HTML report, and compares against a saved baseline. In CI it fails the build on a regression. It also tells you whether to trust its own LLM judge by measuring agreement with your hand labels.

> **Provenance:** a clean reimplementation of a project I originally built; the original code was unavailable, so this was rebuilt from the original design. All 15 tests pass, including an end-to-end test that breaks a fake app on purpose and checks the CLI exits 1, then exits 0 after the revert. The LLM-judge path and the `anthropic` target have **not** been run against the live API yet, and no judge-agreement number is reported.

## Features
- **Targets:** `http` (templated JSON body + dotted output path), `python` (`package.module:function`), `anthropic` (system prompt + model).
- **Graders:** `contains`, `contains_any`, `not_contains`, `regex`, `json_valid` (with required keys), `max_chars`, `latency_ms_max`, and `llm_rubric` (LLM-as-judge that writes its reason *before* the verdict). Adding one is a single decorated function.
- **Repeats:** run each case N times; a case that passes 2 of 3 is flaky, which a single run would hide.
- **Cache + concurrency:** results are keyed by target config, input and repeat, so an unchanged suite makes zero model calls on re-run; `--no-cache` forces fresh calls.
- **Statistics:** the report shows the pass rate with a 95% Wilson interval, because on 20 cases a drop from 90% to 85% is noise.
- **Baseline comparison:** per-case regressions/improvements, exit code 1 on regression (or an overall drop above 2 points).
- **Judge agreement:** `llmeval agreement` runs the judge on outputs you labeled by hand and reports accuracy and Cohen's kappa.

## Install and use
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
export ANTHROPIC_API_KEY=...        # only needed for the judge and the anthropic target

llmeval run examples/prompt_suite.yml --repeats 3 --save-as-baseline eval/baseline.json
llmeval run examples/prompt_suite.yml --repeats 3 --baseline eval/baseline.json   # exit 1 on regression
llmeval agreement examples/suite.yml examples/labels.yml
open runs/report.html
```

### Prove it works by breaking something on purpose
1. Make a suite on an `anthropic` target with a good system prompt and save the baseline.
2. Worsen the prompt (for example "Answer in one word") and run with `--baseline`. It must print regressions and exit 1.
3. Revert the prompt. It must exit 0. (The automated version of this is `tests/test_end_to_end.py`.)

### CI
`.github/workflows/eval.yml` runs the unit tests on every pull request and, once `eval/baseline.json` is committed, runs the suite against it.

## Layout
```
src/llmeval/  suite.py targets.py graders.py judge.py cache.py runner.py stats.py compare.py report.py cli.py
examples/     suite.yml (HTTP/RAG), prompt_suite.yml (bare prompt), labels.yml (judge agreement)
tests/        graders, stats, comparison, and an end-to-end regression test against a fake app
```

## Roadmap
- Embedding-similarity grader
- Pairwise judge with randomized order to cancel position bias
- Token and cost tracking per case; trend chart across saved runs
