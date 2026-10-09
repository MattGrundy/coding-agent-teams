#!/usr/bin/env python3
"""One session across two projects vs two contract-mediated sessions.

Regime `single`: one session sees both repos and makes both changes.
Regime `split` : producer session writes a contract note; consumer session sees
                 only that note and its own repo, never the producer's code.
Scored on integration pass/fail, total cost, total tokens, and peak per-session context.
"""
import argparse, json, pathlib, re, shutil, subprocess, sys, time

H = pathlib.Path(__file__).parent
TEMPLATE = H / "template"

def claude(prompt, cwd, add_dirs=(), model="sonnet", timeout=600):
    cmd = ["claude", "-p", prompt, "--model", model,
           "--output-format", "json", "--permission-mode", "acceptEdits"]
    for d in add_dirs:
        cmd += ["--add-dir", str(d)]
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"cost": 0.0, "tokens": 0, "error": "timeout"}
    m = re.search(r'\{.*\}', p.stdout, re.S)
    if not m:
        return {"cost": 0.0, "tokens": 0, "error": (p.stderr or p.stdout)[:200]}
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"cost": 0.0, "tokens": 0, "error": "unparseable json"}
    u = obj.get("usage", {}) or {}
    tokens = (u.get("input_tokens", 0) + u.get("output_tokens", 0)
              + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0))
    # Context occupancy = the largest single-turn input, NOT the sum across turns.
    # Summing counts cache_read again every turn, which scores a many-turn session as
    # "bloated" when it may be holding very little.
    peak_ctx = 0
    for it in (u.get("iterations") or []):
        peak_ctx = max(peak_ctx, it.get("input_tokens", 0)
                       + it.get("cache_read_input_tokens", 0)
                       + it.get("cache_creation_input_tokens", 0))
    if not peak_ctx:
        peak_ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                    + u.get("cache_creation_input_tokens", 0))
    return {"cost": obj.get("total_cost_usd", 0.0), "tokens": tokens,
            "peak_ctx": peak_ctx, "turns": len(u.get("iterations") or []) or 1,
            "out": u.get("output_tokens", 0), "error": None}

def fresh(dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(TEMPLATE, dst)
    (dst / "contract").mkdir(exist_ok=True)
    return dst

def run_single(work, task_dir, model):
    prompt = f"""This working directory contains two services that talk to each other over a JSON event.

`producer/` emits the event. `consumer/` parses it and renders a line.
They are separate services; the JSON is the contract between them.

Make BOTH of the following changes so the two sides still work together end to end.

## Change required in producer/
{(task_dir / 'producer.md').read_text()}
## Change required in consumer/
{(task_dir / 'consumer.md').read_text()}
Edit the files. Do not explain, just make the changes."""
    r = claude(prompt, work, model=model)
    return [r]

def run_split(work, task_dir, model):
    contract = work / "contract"
    p_prompt = f"""You maintain `producer/`, a service that emits a JSON event consumed by another
team's service. You CANNOT see the consumer's code and must not guess at it.

## Your change
{(task_dir / 'producer.md').read_text()}
Edit the files in producer/.

Then write `{contract}/CONTRACT.md` describing the wire format you now emit, precisely
enough that the consuming team can update their parser without seeing your code.
Do not explain, just make the changes and write the note."""
    r1 = claude(p_prompt, work / "producer", add_dirs=[contract], model=model)

    c_prompt = f"""You maintain `consumer/`, a service that parses a JSON event emitted by another
team's service. You CANNOT see the producer's code.

The producing team has described their wire format in `{contract}/CONTRACT.md`. Read it.

## Your change
{(task_dir / 'consumer.md').read_text()}
Edit the files in consumer/. Do not explain, just make the changes."""
    r2 = claude(c_prompt, work / "consumer", add_dirs=[contract], model=model)
    return [r1, r2]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=3)
    a = ap.parse_args()

    tasks = sorted(d for d in (H / "tasks").iterdir() if d.is_dir())
    out = H / "results"; out.mkdir(exist_ok=True)
    recs = []
    with (out / "runs.jsonl").open("w") as fh:
        for task in tasks:
            for regime in ("single", "split"):
                for i in range(a.runs):
                    work = fresh(H / "work" / task.name / regime / str(i))
                    t0 = time.time()
                    sessions = (run_single if regime == "single" else run_split)(work, task, a.model)
                    chk = subprocess.run([sys.executable, str(task / "check.py"), str(work)],
                                         capture_output=True, text=True)
                    rec = {"task": task.name, "regime": regime, "run": i,
                           "passed": chk.returncode == 0,
                           "detail": chk.stdout.strip()[:300],
                           "sessions": len(sessions),
                           "cost": round(sum(s["cost"] for s in sessions), 4),
                           "tokens": sum(s["tokens"] for s in sessions),
                           "peak_session_tokens": max((s["tokens"] for s in sessions), default=0),
                           "peak_ctx": max((s.get("peak_ctx", 0) for s in sessions), default=0),
                           "turns": sum(s.get("turns", 1) for s in sessions),
                           "errors": [s["error"] for s in sessions if s["error"]],
                           "secs": round(time.time() - t0, 1)}
                    recs.append(rec)
                    fh.write(json.dumps(rec) + "\n"); fh.flush()
                    print(f"{task.name:<18}{regime:<8}run{i}  "
                          f"{'PASS' if rec['passed'] else 'FAIL'}  "
                          f"${rec['cost']:<8} {rec['tokens']:>7}tok  peakctx {rec['peak_ctx']:>7}  turns {rec['turns']:>2}",
                          file=sys.stderr)
    print(f"wrote {out/'runs.jsonl'} ({len(recs)} runs)")

if __name__ == "__main__":
    main()
