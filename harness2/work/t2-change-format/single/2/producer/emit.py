import json, sys
from datetime import datetime, timezone

def build_event():
    """The event this service emits. `ts` is an RFC3339 UTC string."""
    ts = datetime.fromtimestamp(1750000000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"id": "evt-1", "ts": ts, "status": "ok"}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
