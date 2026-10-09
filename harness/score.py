#!/usr/bin/env python3
"""Score results/runs.jsonl against the planted ground truth."""
import collections, json, pathlib

HERE = pathlib.Path(__file__).parent

def majority(verdicts):
    """Majority verdict across runs; None if unparseable dominates."""
    c = collections.Counter(v for v in verdicts if v)
    if not c:
        return None
    return c.most_common(1)[0][0]

def main():
    truth = {}
    for d in sorted((HERE / "cases").iterdir()):
        if d.is_dir():
            t = json.loads((d / "truth.json").read_text())
            truth[t["id"]] = t

    runs = [json.loads(l) for l in (HERE / "results" / "runs.jsonl").read_text().splitlines() if l.strip()]
    by = collections.defaultdict(list)
    for r in runs:
        by[(r["case"], r["reviewer"])].append(r["verdict"])

    verdict = {k: majority(v) for k, v in by.items()}

    # per-run instability
    flips = sum(1 for k, v in by.items() if len(set(x for x in v if x)) > 1)
    unparsed = sum(1 for r in runs if r["verdict"] is None)

    defective = [c for c in truth if truth[c]["defective"]]
    clean = [c for c in truth if not truth[c]["defective"]]

    def caught(case, rev):
        return verdict.get((case, rev)) == "block"

    rows = []
    for c in sorted(truth):
        a, b = verdict.get((c, "a")), verdict.get((c, "b"))
        # critique (B) IS the gate; code-review (A) is a secondary lens, not the gate.
        gate = b if b in ("pass", "block") else "pass"
        d = truth[c]["defective"]
        rows.append((c, truth[c]["class"], "defective" if d else "clean", a, b, gate,
                     "MISS" if (d and gate == "pass") else ("FALSE-BLOCK" if (not d and gate == "block") else "ok")))

    print(f"{'case':<26}{'class':<20}{'truth':<11}{'A':<7}{'B':<7}{'gate':<7}outcome")
    print("-" * 92)
    for r in rows:
        print(f"{r[0]:<26}{r[1]:<20}{r[2]:<11}{str(r[3]):<7}{str(r[4]):<7}{str(r[5]):<7}{r[6]}")

    a_catch = sum(1 for c in defective if caught(c, "a"))
    b_catch = sum(1 for c in defective if caught(c, "b"))
    gate_catch = sum(1 for c in defective if caught(c, "b"))
    both_miss = [c for c in defective if not caught(c, "a") and not caught(c, "b")]
    a_only = [c for c in defective if caught(c, "a") and not caught(c, "b")]
    b_only = [c for c in defective if caught(c, "b") and not caught(c, "a")]
    both_catch = [c for c in defective if caught(c, "a") and caught(c, "b")]

    a_fp = sum(1 for c in clean if caught(c, "a"))
    b_fp = sum(1 for c in clean if caught(c, "b"))
    gate_fp = sum(1 for c in clean if caught(c, "b"))

    nd, nc = len(defective), len(clean)
    print(f"\ncases: {nd} defective, {nc} clean | runs/pair: {len(next(iter(by.values())))} "
          f"| unstable pairs: {flips} | unparsed calls: {unparsed}")
    print(f"\ncatch rate on defective   code-review {a_catch}/{nd}   critique {b_catch}/{nd}   GATE(critique) {gate_catch}/{nd}")
    print(f"false blocks on clean     code-review {a_fp}/{nc}   critique {b_fp}/{nc}   GATE(critique) {gate_fp}/{nc}")
    print(f"\nvalue of the second lens: {len(a_only)}/{nd} defects code-review caught that the gate missed")

    print(f"\noverlap on the {nd} defective cases:")
    print(f"  both caught : {len(both_catch)}  {sorted(both_catch)}")
    print(f"  A only      : {len(a_only)}  {sorted(a_only)}")
    print(f"  B only      : {len(b_only)}  {sorted(b_only)}")
    print(f"  both missed : {len(both_miss)}  {sorted(both_miss)}")

    # The headline: of everything the gate waved through, how much was defective?
    passed = [c for c in truth if verdict.get((c, "b")) == "pass"]
    bad_passed = [c for c in passed if truth[c]["defective"]]
    if passed:
        print(f"\n2/2 false-clear rate: {len(bad_passed)}/{len(passed)} "
              f"({100*len(bad_passed)/len(passed):.0f}%) of diffs the gate cleared were defective")
        if bad_passed:
            print(f"  cleared but defective: {sorted(bad_passed)}")

    # Independence: are the two reviewers' misses correlated?
    pa_miss, pb_miss = (nd - a_catch) / nd, (nd - b_catch) / nd
    expected = pa_miss * pb_miss * nd
    print(f"\nindependence check on misses:")
    print(f"  A miss rate {pa_miss:.2f}, B miss rate {pb_miss:.2f}")
    print(f"  both-miss expected if independent: {expected:.1f}/{nd}")
    print(f"  both-miss observed:                {len(both_miss)}/{nd}")
    if expected > 0:
        print(f"  ratio observed/expected: {len(both_miss)/expected:.2f}x  (>1 = correlated failure)")

if __name__ == "__main__":
    main()
