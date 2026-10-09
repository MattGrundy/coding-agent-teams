#!/usr/bin/env python3
"""Score the cross-project eval: correctness, cost, and context occupancy by regime."""
import collections, json, pathlib, statistics as st

H = pathlib.Path(__file__).parent

def med(xs):
    return st.median(xs) if xs else 0

def main():
    runs = [json.loads(l) for l in (H / "results" / "runs.jsonl").read_text().splitlines() if l.strip()]
    by = collections.defaultdict(list)
    for r in runs:
        by[(r["task"], r["regime"])].append(r)

    tasks = sorted({r["task"] for r in runs})
    print(f"{'task':<20}{'regime':<9}{'pass':<8}{'cost $':<10}{'tokens':<10}{'peak ctx':<10}{'turns':<7}")
    print("-" * 74)
    for t in tasks:
        for reg in ("single", "split"):
            rs = by[(t, reg)]
            if not rs:
                continue
            p = sum(1 for r in rs if r["passed"])
            print(f"{t:<20}{reg:<9}{p}/{len(rs):<6}"
                  f"{med([r['cost'] for r in rs]):<10.4f}"
                  f"{med([r['tokens'] for r in rs]):<10.0f}"
                  f"{med([r.get('peak_ctx', 0) for r in rs]):<10.0f}"
                  f"{med([r.get('turns', 1) for r in rs]):<7.0f}")

    print()
    agg = {}
    for reg in ("single", "split"):
        rs = [r for r in runs if r["regime"] == reg]
        agg[reg] = {
            "n": len(rs),
            "pass": sum(1 for r in rs if r["passed"]),
            "cost": med([r["cost"] for r in rs]),
            "tokens": med([r["tokens"] for r in rs]),
            "peak": med([r.get("peak_ctx", 0) for r in rs]),
            "turns": med([r.get("turns", 1) for r in rs]),
        }
    for reg in ("single", "split"):
        a = agg[reg]
        print(f"{reg:<8} n={a['n']:<3} passed {a['pass']}/{a['n']}   "
              f"median cost ${a['cost']:.4f}   median tokens {a['tokens']:.0f}   "
              f"median peak ctx {a['peak']:.0f}")

    s, p = agg["single"], agg["split"]
    print()
    if s["cost"]:
        print(f"cost:      split is {p['cost']/s['cost']:.2f}x single")
    if s["peak"]:
        print(f"peak ctx:  split is {p['peak']/s['peak']:.2f}x single "
              f"({'LOWER per session' if p['peak'] < s['peak'] else 'HIGHER per session'})")
    print(f"pass rate: single {s['pass']}/{s['n']}, split {p['pass']}/{p['n']}")

    fails = [r for r in runs if not r["passed"]]
    if fails:
        print(f"\nfailures ({len(fails)}):")
        for r in fails:
            print(f"  {r['task']} {r['regime']} run{r['run']}: {r['detail'][:160]}")
    errs = [r for r in runs if r.get("errors")]
    if errs:
        print(f"\nsession errors ({len(errs)}):")
        for r in errs:
            print(f"  {r['task']} {r['regime']} run{r['run']}: {r['errors']}")

if __name__ == "__main__":
    main()
