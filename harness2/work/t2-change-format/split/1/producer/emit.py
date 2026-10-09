import json, sys
from datetime import datetime, timezone

def to_rfc3339_utc(unix_seconds):
    """Format unix seconds as RFC3339 UTC, e.g. 2001-02-03T04:05:06Z."""
    dt = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def build_event():
    """The event this service emits."""
    return {"id": "evt-1", "ts": to_rfc3339_utc(1750000000), "status": "ok"}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
