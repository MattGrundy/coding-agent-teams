#!/usr/bin/env python3
"""Cumulative integration check: every change so far must still hold."""
import datetime, subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
RFC = datetime.datetime.fromtimestamp(1750000000, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
expected = f"[evt-1] ok at {RFC} retries: 3"
try:
    p = subprocess.run([sys.executable, str(root/"producer"/"emit.py")], capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        print(f"FAIL producer exited {p.returncode}: {p.stderr.strip()[:200]}"); sys.exit(1)
    c = subprocess.run([sys.executable, str(root/"consumer"/"render.py")], input=p.stdout,
                       capture_output=True, text=True, timeout=30)
    if c.returncode != 0:
        print(f"FAIL consumer exited {c.returncode}: {c.stderr.strip()[:200]}"); sys.exit(1)
except subprocess.TimeoutExpired:
    print("FAIL timeout"); sys.exit(1)
got = c.stdout.strip()
if got == expected:
    print("PASS"); sys.exit(0)
print(f"FAIL\n  expected: {expected!r}\n  got:      {got!r}"); sys.exit(1)
