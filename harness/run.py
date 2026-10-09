#!/usr/bin/env python3
"""Run each reviewer over each case N times via `claude -p`. Writes results/runs.jsonl."""
import argparse, concurrent.futures as cf, json, pathlib, re, subprocess, sys, time

HERE = pathlib.Path(__file__).parent

def build_prompt(brief, case_dir):
    task = (case_dir / "task.md").read_text()
    diff = (case_dir / "diff.patch").read_text()
    ctx = case_dir / "context.md"
    parts = [brief, "\n---\n\n## The task the author was given\n\n", task,
             "\n## The diff under review\n\n```diff\n", diff, "\n```\n"]
    if ctx.exists():
        parts += ["\n## Surrounding code\n\n```go\n", ctx.read_text(), "\n```\n"]
    parts.append("\nRespond with only the JSON object.")
    return "".join(parts)

def parse_verdict(out):
    m = re.search(r'\{.*?"verdict".*?\}', out, re.S)
    if not m:
        return None, out.strip()[:200]
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None, m.group(0)[:200]
    v = str(obj.get("verdict", "")).lower().strip()
    return (v if v in ("pass", "block") else None), obj.get("reason", "")

def one(case_dir, reviewer, brief, model, run_idx):
    prompt = build_prompt(brief, case_dir)
    t0 = time.time()
    try:
        p = subprocess.run(["claude", "-p", prompt, "--model", model],
                           capture_output=True, text=True, timeout=180)
        verdict, reason = parse_verdict(p.stdout)
    except subprocess.TimeoutExpired:
        verdict, reason = None, "TIMEOUT"
    return {"case": case_dir.name, "reviewer": reviewer, "run": run_idx,
            "verdict": verdict, "reason": reason, "secs": round(time.time() - t0, 1)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    briefs = {n: (HERE / "reviewers" / f"{n}.md").read_text() for n in ("a", "b")}
    cases = sorted(d for d in (HERE / "cases").iterdir() if d.is_dir())
    jobs = [(c, r, briefs[r], a.model, i)
            for c in cases for r in ("a", "b") for i in range(a.runs)]
    print(f"{len(cases)} cases x 2 reviewers x {a.runs} runs = {len(jobs)} calls, model={a.model}")

    out = HERE / "results"; out.mkdir(exist_ok=True)
    done = 0
    with (out / "runs.jsonl").open("w") as fh, \
         cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for rec in ex.map(lambda j: one(*j), jobs):
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            done += 1
            print(f"  [{done}/{len(jobs)}] {rec['case']:<24} {rec['reviewer']} "
                  f"-> {rec['verdict']} ({rec['secs']}s)", file=sys.stderr)
    print(f"wrote {out/'runs.jsonl'}")

if __name__ == "__main__":
    main()
