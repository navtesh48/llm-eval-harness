import time, json, importlib, httpx
from llmeval.suite import Target

def _render(obj, text):
    if isinstance(obj, str): return obj.replace('{{input}}', text)
    if isinstance(obj, dict): return {k: _render(v, text) for k, v in obj.items()}
    if isinstance(obj, list): return [_render(v, text) for v in obj]
    return obj

def _dig(obj, path: str):
    for part in path.split('.'):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj

def call(t: Target, text: str) -> tuple[str, float]:
    """Call the system under test. Returns (output text, latency in ms)."""
    t0 = time.perf_counter()
    if t.type == 'http':
        r = httpx.post(t.url, json=_render(t.body or {}, text), timeout=120); r.raise_for_status()
        out = r.json(); out = _dig(out, t.output_path) if t.output_path else out
    elif t.type == 'python':
        mod, fn = t.callable.split(':'); out = getattr(importlib.import_module(mod), fn)(text)
    else:
        from anthropic import Anthropic
        resp = Anthropic().messages.create(model=t.model or 'claude-sonnet-5-5', max_tokens=t.max_tokens,
                                           system=t.system or '', messages=[{'role': 'user', 'content': text}])
        out = ''.join(b.text for b in resp.content if b.type == 'text')
    ms = (time.perf_counter() - t0) * 1000
    return (out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)), ms
