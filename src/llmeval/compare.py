from llmeval.runner import case_rates

def compare(base: dict, cur: dict, tolerance: float = 0.0, max_drop: float = 0.02) -> dict:
    b, c = case_rates(base), case_rates(cur)
    common = sorted(set(b) & set(c))
    regress = [k for k in common if b[k] - c[k] > tolerance]
    improve = [k for k in common if c[k] - b[k] > tolerance]
    bm = sum(b[k] for k in common) / max(1, len(common)); cm = sum(c[k] for k in common) / max(1, len(common))
    return dict(regressions=regress, improvements=improve, base_rate=bm, cur_rate=cm, new_cases=sorted(set(c) - set(b)),
                failed=bool(regress) or (bm - cm) > max_drop)
