import json, sys

def build_event():
    """The event this service emits."""
    return {"id": "evt-1", "ts": 1750000000, "status": "ok", "retry_count": 3}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
