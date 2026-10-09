#!/usr/bin/env python3
"""Cumulative task sequence: each task lands on top of the last, so the check grows."""
import pathlib, textwrap

H = pathlib.Path(__file__).parent

SEQ = [
{"name":"01-add-field",
 "producer":"The event should carry how many times it was retried before being emitted. In the sample event that value is 3. Add it to the emitted event. You choose the field name.",
 "consumer":"The event now carries a retry count. Append it to the rendered line as ` retries: N` (one leading space, the literal `retries: `, then the number).",
 "expected":'f"[evt-1] ok at 1750000000 retries: 3"'},
{"name":"02-change-format",
 "producer":"The event's timestamp is currently a unix integer. Emit it as an RFC3339 string in UTC instead, representing the same instant. You choose whether to keep the field name.",
 "consumer":"The event's timestamp is now an RFC3339 string in UTC rather than a unix integer. Render it as-is, in the same position in the line.",
 "expected":'f"[evt-1] ok at {RFC} retries: 3"'},
{"name":"03-split-field",
 "producer":"The event's `status` collapses two things: the state, and why it is in that state. Split them. In the sample the state is `ok` and the reason is `healthy`. You choose the field names.",
 "consumer":"The event now carries state and reason separately. Render them as `state (reason)` where the status currently appears.",
 "expected":'f"[evt-1] ok (healthy) at {RFC} retries: 3"'},
]

CHECK = '''#!/usr/bin/env python3
"""Cumulative integration check: every change so far must still hold."""
import datetime, subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
RFC = datetime.datetime.fromtimestamp(1750000000, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
expected = {expected}
try:
    p = subprocess.run([sys.executable, str(root/"producer"/"emit.py")], capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        print(f"FAIL producer exited {{p.returncode}}: {{p.stderr.strip()[:200]}}"); sys.exit(1)
    c = subprocess.run([sys.executable, str(root/"consumer"/"render.py")], input=p.stdout,
                       capture_output=True, text=True, timeout=30)
    if c.returncode != 0:
        print(f"FAIL consumer exited {{c.returncode}}: {{c.stderr.strip()[:200]}}"); sys.exit(1)
except subprocess.TimeoutExpired:
    print("FAIL timeout"); sys.exit(1)
got = c.stdout.strip()
if got == expected:
    print("PASS"); sys.exit(0)
print(f"FAIL\\n  expected: {{expected!r}}\\n  got:      {{got!r}}"); sys.exit(1)
'''

for i, s in enumerate(SEQ):
    d = H / "tasks" / s["name"]
    d.mkdir(parents=True, exist_ok=True)
    (d/"producer.md").write_text(s["producer"] + "\n")
    (d/"consumer.md").write_text(s["consumer"] + "\n")
    (d/"check.py").write_text(CHECK.format(expected=s["expected"]))
print(f"built {len(SEQ)} cumulative tasks")
