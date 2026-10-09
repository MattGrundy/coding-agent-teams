import json, sys

def build_event():
    """The event this service emits."""
    return {
        "id": "evt-1",
        "ts": 1750000000,
        "status": "ok",
        "status_reason": "healthy",
    }

if __name__ == "__main__":
    json.dump(build_event(), sys.stdout)
