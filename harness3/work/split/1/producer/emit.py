import json, sys
from datetime import datetime, timezone

def to_rfc3339(epoch_seconds):
    """Unix seconds -> RFC3339 UTC string, e.g. 2025-06-15T15:06:40Z."""
    dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def build_event():
    """The event this service emits."""
    return {"id": "evt-1", "ts": to_rfc3339(1750000000), "status": "ok", "status_reason": "healthy", "retry_count": 3}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
