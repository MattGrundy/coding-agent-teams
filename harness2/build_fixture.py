#!/usr/bin/env python3
"""Create the template repos + task specs for the cross-project eval."""
import pathlib, textwrap

H = pathlib.Path(__file__).parent
T = H / "template"

FILES = {
"producer/emit.py": '''\
import json, sys

def build_event():
    """The event this service emits."""
    return {"id": "evt-1", "ts": 1750000000, "status": "ok"}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
''',
"producer/README.md": '''\
# producer

Emits a single JSON event on stdout. Downstream services parse it.
The wire format is a contract: changing a field name breaks consumers.
''',
"consumer/render.py": '''\
import json, sys

def render(e):
    """Render one event as a human-readable line."""
    return f"[{e['id']}] {e['status']} at {e['ts']}"

if __name__ == "__main__":
    print(render(json.load(sys.stdin)))
''',
"consumer/README.md": '''\
# consumer

Reads one JSON event on stdin and prints a human-readable line.
The wire format is produced by another service, maintained by another team.
''',
}

TASKS = {
"t1-add-field": {
  "producer": textwrap.dedent('''\
      The event should carry how many times it was retried before being emitted.
      In the sample event that value is 3.

      Add it to the emitted event. You choose the field name.
      '''),
  "consumer": textwrap.dedent('''\
      The event now carries a retry count. Append it to the rendered line as
      ` retries: N` (a single leading space, then the literal `retries: `, then the number).

      So a line that currently reads `[evt-1] ok at 1750000000` should read
      `[evt-1] ok at 1750000000 retries: 3`.
      '''),
  "check": '''\
expected = "[evt-1] ok at 1750000000 retries: 3"
''' },

"t2-change-format": {
  "producer": textwrap.dedent('''\
      The event's timestamp is currently a unix integer. Emit it as an RFC3339
      string in UTC instead (e.g. 2001-02-03T04:05:06Z), representing the same instant.

      You choose whether to keep the same field name.
      '''),
  "consumer": textwrap.dedent('''\
      The event's timestamp is now an RFC3339 string in UTC rather than a unix
      integer. Render it as-is, in the same position in the line.

      So a line that currently reads `[evt-1] ok at 1750000000` should read
      `[evt-1] ok at <the RFC3339 string>`.
      '''),
  "check": '''\
import datetime
ts = datetime.datetime.fromtimestamp(1750000000, datetime.timezone.utc)
expected = f"[evt-1] ok at {ts.strftime('%Y-%m-%dT%H:%M:%SZ')}"
''' },

"t3-split-field": {
  "producer": textwrap.dedent('''\
      The event's `status` currently collapses two things: the state, and why it is
      in that state. Split them. In the sample event the state is `ok` and the
      reason is `healthy`.

      You choose the field names.
      '''),
  "consumer": textwrap.dedent('''\
      The event now carries the state and the reason for it separately. Render them
      as `state (reason)` where the status currently appears.

      So a line that currently reads `[evt-1] ok at 1750000000` should read
      `[evt-1] ok (healthy) at 1750000000`.
      '''),
  "check": '''\
expected = "[evt-1] ok (healthy) at 1750000000"
''' },
}

CHECK = '''\
#!/usr/bin/env python3
"""Integration check: producer output must feed consumer and render the expected line."""
import subprocess, sys, pathlib

root = pathlib.Path(sys.argv[1])
{expected_block}
try:
    p = subprocess.run([sys.executable, str(root / "producer" / "emit.py")],
                       capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        print(f"FAIL producer exited {{p.returncode}}: {{p.stderr.strip()[:200]}}"); sys.exit(1)
    c = subprocess.run([sys.executable, str(root / "consumer" / "render.py")],
                       input=p.stdout, capture_output=True, text=True, timeout=30)
    if c.returncode != 0:
        print(f"FAIL consumer exited {{c.returncode}}: {{c.stderr.strip()[:200]}}"); sys.exit(1)
except subprocess.TimeoutExpired:
    print("FAIL timeout"); sys.exit(1)

got = c.stdout.strip()
if got == expected:
    print("PASS"); sys.exit(0)
print(f"FAIL\\n  expected: {{expected!r}}\\n  got:      {{got!r}}"); sys.exit(1)
'''

def main():
    for rel, body in FILES.items():
        p = T / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    for name, spec in TASKS.items():
        d = H / "tasks" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "producer.md").write_text(spec["producer"])
        (d / "consumer.md").write_text(spec["consumer"])
        (d / "check.py").write_text(CHECK.format(expected_block=spec["check"]))
    print(f"template -> {T}")
    print(f"tasks    -> {H/'tasks'} ({len(TASKS)})")

if __name__ == "__main__":
    main()
