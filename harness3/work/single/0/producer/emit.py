import json, sys
from datetime import datetime, timezone

def build_event():
    """The event this service emits."""
    ts = datetime.fromtimestamp(1750000000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"id": "evt-1", "ts": ts, "state": "ok", "reason": "healthy","retry_count": 3}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
