import json, sys
from datetime import datetime, timezone

def to_rfc3339(unix_seconds):
    return datetime.fromtimestamp(unix_seconds, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_event():
    """The event this service emits."""
    return {"id": "evt-1", "ts": to_rfc3339(1750000000), "state": "ok", "reason": "healthy","retry_count": 3}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
