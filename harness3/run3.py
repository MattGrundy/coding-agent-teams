#!/usr/bin/env python3
"""Simulated-real regime: long-lived sessions working a SEQUENCE of coordinated tasks.

single : one persistent session holding both repos, resumed across every task.
split  : two persistent leads (producer, consumer), each resumed inside its own repo,
         exchanging a written contract at each boundary. Neither ever sees the other's code.

Per task we record cost, tokens and peak single-turn context, so the growth curve is visible.
"""
import argparse, json, pathlib, re, shutil, subprocess, sys, time

H = pathlib.Path(__file__).parent
TEMPLATE = H / "template"

def claude(prompt, cwd, resume=None, add_dirs=(), model="sonnet", timeout=900):
    cmd = ["claude", "-p", prompt, "--model", model,
           "--output-format", "json", "--permission-mode", "acceptEdits"]
    if resume:
        cmd += ["--resume", resume]
    for d in add_dirs:
        cmd += ["--add-dir", str(d)]
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"cost":0.0,"tokens":0,"peak_ctx":0,"sid":resume,"error":"timeout"}
    m = re.search(r'\{.*\}', p.stdout, re.S)
    if not m:
        return {"cost":0.0,"tokens":0,"peak_ctx":0,"sid":resume,"error":(p.stderr or p.stdout)[:200]}
    try:
        o = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"cost":0.0,"tokens":0,"peak_ctx":0,"sid":resume,"error":"unparseable"}
    u = o.get("usage", {}) or {}
    tokens = (u.get("input_tokens",0) + u.get("output_tokens",0)
              + u.get("cache_creation_input_tokens",0) + u.get("cache_read_input_tokens",0))
    peak = 0
    for it in (u.get("iterations") or []):
        peak = max(peak, it.get("input_tokens",0) + it.get("cache_read_input_tokens",0)
                        + it.get("cache_creation_input_tokens",0))
    if not peak:
        peak = (u.get("input_tokens",0) + u.get("cache_read_input_tokens",0)
                + u.get("cache_creation_input_tokens",0))
    return {"cost":o.get("total_cost_usd",0.0), "tokens":tokens, "peak_ctx":peak,
            "sid":o.get("session_id") or resume, "error":None}

def fresh(dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(TEMPLATE, dst)
    (dst/"contract").mkdir(exist_ok=True)
    return dst

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=2)
    a = ap.parse_args()

    tasks = sorted(d for d in (H/"tasks").iterdir() if d.is_dir())
    out = H/"results"; out.mkdir(exist_ok=True)

    with (out/"runs.jsonl").open("w") as fh:
        for regime in ("single","split"):
            for run in range(a.runs):
                work = fresh(H/"work"/regime/str(run))
                sid_single = sid_prod = sid_cons = None
                for idx, task in enumerate(tasks):
                    t0 = time.time()
                    if regime == "single":
                        prompt = f"""This directory holds two services, `producer/` and `consumer/`, that talk over a JSON event.
The JSON is the contract between them. Make BOTH changes below so they still work end to end.

## producer/
{(task/'producer.md').read_text()}
## consumer/
{(task/'consumer.md').read_text()}
Edit the files. Do not explain."""
                        r = claude(prompt, work, resume=sid_single, model=a.model)
                        sid_single = r["sid"]
                        sessions = [r]
                    else:
                        contract = work/"contract"
                        note = contract/f"CONTRACT-{idx+1}.md"
                        p_prompt = f"""You maintain `producer/`. Another team consumes your JSON event. You CANNOT see their code.

## Your change
{(task/'producer.md').read_text()}
Edit producer/. Then write `{note}` describing the wire format you now emit, precisely enough
that the consuming team can update their parser without seeing your code. Do not explain."""
                        r1 = claude(p_prompt, work/"producer", resume=sid_prod,
                                    add_dirs=[contract], model=a.model)
                        sid_prod = r1["sid"]
                        c_prompt = f"""You maintain `consumer/`. Another team produces the JSON event you parse. You CANNOT see their code.
They have described the new wire format in `{note}`. Read it.

## Your change
{(task/'consumer.md').read_text()}
Edit consumer/. Do not explain."""
                        r2 = claude(c_prompt, work/"consumer", resume=sid_cons,
                                    add_dirs=[contract], model=a.model)
                        sid_cons = r2["sid"]
                        sessions = [r1, r2]

                    chk = subprocess.run([sys.executable, str(task/"check.py"), str(work)],
                                         capture_output=True, text=True)
                    rec = {"regime":regime, "run":run, "task_index":idx+1, "task":task.name,
                           "passed":chk.returncode==0, "detail":chk.stdout.strip()[:300],
                           "cost":round(sum(s["cost"] for s in sessions),4),
                           "tokens":sum(s["tokens"] for s in sessions),
                           "peak_ctx":max(s["peak_ctx"] for s in sessions),
                           "errors":[s["error"] for s in sessions if s["error"]],
                           "secs":round(time.time()-t0,1)}
                    fh.write(json.dumps(rec)+"\n"); fh.flush()
                    print(f"{regime:<8}run{run} task{idx+1} "
                          f"{'PASS' if rec['passed'] else 'FAIL'} ${rec['cost']:<8} "
                          f"peakctx {rec['peak_ctx']:>7}", file=sys.stderr)
    print("done")

if __name__ == "__main__":
    main()
