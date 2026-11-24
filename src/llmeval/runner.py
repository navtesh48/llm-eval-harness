import subprocess, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from llmeval.suite import Suite
from llmeval.targets import call
from llmeval.graders import grade
from llmeval.cache import key, cached

def _git_sha() -> str:
    try: return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception: return 'unknown'

def run_suite(suite: Suite, repeats: int = 1, concurrency: int = 8, use_cache: bool = True) -> dict:
    """Run every case `repeats` times. Repeats matter: a case that passes 2 of 3 times is flaky,
    and a single run would hide that."""
    def one(job):
        case, r = job
        try:
            out, ms = cached(key('target', suite.target.model_dump(), case.input, r), lambda: list(call(suite.target, case.input)), use_cache)
            ctx = {'input': case.input, 'latency_ms': ms, 'use_cache': use_cache}
            grades = [dict(type=gs.type, **vars(grade(out, gs, ctx))) for gs in case.graders]
            return dict(case_id=case.id, tags=case.tags, repeat=r, output=out, latency_ms=ms, grades=grades,
                        passed=all(g['passed'] for g in grades))
        except Exception as e:
            return dict(case_id=case.id, tags=case.tags, repeat=r, output='', latency_ms=0, error=str(e),
                        grades=[], passed=False)
    jobs = [(c, r) for c in suite.cases for r in range(repeats)]
    with ThreadPoolExecutor(concurrency) as ex: results = list(ex.map(one, jobs))
    return dict(suite=suite.name, ts=dt.datetime.now(dt.timezone.utc).isoformat(), git=_git_sha(), repeats=repeats, results=results)

def case_rates(run: dict) -> dict[str, float]:
    by: dict[str, list[bool]] = {}
    for r in run['results']: by.setdefault(r['case_id'], []).append(r['passed'])
    return {k: sum(v) / len(v) for k, v in by.items()}
