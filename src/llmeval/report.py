import html
from llmeval.runner import case_rates
from llmeval.stats import wilson

def to_html(run: dict, cmp: dict | None = None) -> str:
    k = sum(r['passed'] for r in run['results']); n = len(run['results'])
    lo, hi = wilson(k, n)
    rows = ''
    for r in run['results']:
        color = '#e6f4ea' if r['passed'] else '#fce8e6'
        det = '<br>'.join(html.escape(f"{g['type']}: {'ok' if g['passed'] else 'FAIL'} {g.get('detail', '')}") for g in r['grades']) + html.escape(r.get('error', ''))
        rows += (f"<tr style='background:{color}'><td>{html.escape(r['case_id'])}</td><td>{r['repeat']}</td>"
                 f"<td>{html.escape(r['output'][:600])}</td><td>{det}</td><td>{r['latency_ms']:.0f}</td></tr>")
    banner = ''
    if cmp:
        banner = (f"<p><b>Vs baseline:</b> {cmp['base_rate']:.1%} to {cmp['cur_rate']:.1%}; regressions: "
                  f"{html.escape(', '.join(cmp['regressions']) or 'none')}; improvements: {html.escape(', '.join(cmp['improvements']) or 'none')}</p>")
    return (f"<html><body style='font-family:sans-serif'><h2>{html.escape(run['suite'])} @ {html.escape(run['git'])}</h2>"
            f"<p>Pass rate {k}/{n} = {k/n:.1%} (95% interval {lo:.1%} to {hi:.1%})</p>{banner}"
            f"<table border=1 cellpadding=4><tr><th>case</th><th>rep</th><th>output</th><th>graders</th><th>ms</th></tr>{rows}</table></body></html>")
