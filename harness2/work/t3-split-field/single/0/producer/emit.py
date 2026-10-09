import json, sys

def build_event():
    """The event this service emits."""
    return {"id": "evt-1", "ts": 1750000000, "state": "ok", "reason": "healthy"}

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
