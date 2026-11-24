import argparse, json, pathlib, sys, yaml
from dotenv import load_dotenv
from llmeval.suite import load_suite
from llmeval.runner import run_suite
from llmeval.compare import compare
from llmeval.report import to_html
from llmeval.stats import kappa

def main():
    load_dotenv()
    ap = argparse.ArgumentParser(prog='llmeval'); sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('suite'); r.add_argument('--baseline'); r.add_argument('--repeats', type=int, default=1)
    r.add_argument('--concurrency', type=int, default=8); r.add_argument('--no-cache', action='store_true')
    r.add_argument('--out', default='runs'); r.add_argument('--save-as-baseline')
    a = sub.add_parser('agreement'); a.add_argument('suite'); a.add_argument('labels')
    args = ap.parse_args()

    if args.cmd == 'run':
        run = run_suite(load_suite(args.suite), args.repeats, args.concurrency, not args.no_cache)
        out = pathlib.Path(args.out); out.mkdir(exist_ok=True)
        cmp = None
        if args.baseline:
            cmp = compare(json.load(open(args.baseline)), run)
        (out / 'latest.json').write_text(json.dumps(run, indent=1))
        (out / 'report.html').write_text(to_html(run, cmp))
        if args.save_as_baseline: pathlib.Path(args.save_as_baseline).write_text(json.dumps(run, indent=1))
        k = sum(x['passed'] for x in run['results']); print(f"{k}/{len(run['results'])} passed -> {out/'report.html'}")
        if cmp:
            print(f"baseline {cmp['base_rate']:.1%} -> {cmp['cur_rate']:.1%}; regressions: {cmp['regressions'] or 'none'}")
            sys.exit(1 if cmp['failed'] else 0)
    else:
        from llmeval.judge import judge
        suite = load_suite(args.suite); cases = {c.id: c for c in suite.cases}
        labels = yaml.safe_load(open(args.labels)); human, model = [], []
        for l in labels:
            spec = next(g for g in cases[l['case_id']].graders if g.type == 'llm_rubric')
            human.append(bool(l['human_pass'])); model.append(judge(cases[l['case_id']].input, l['output'], spec.model_dump()['rubric']).passed)
        acc = sum(h == m for h, m in zip(human, model)) / len(human)
        print(f'judge agreement: accuracy {acc:.2f}, kappa {kappa(human, model):.2f} over {len(human)} labels')

if __name__ == '__main__':
    main()
