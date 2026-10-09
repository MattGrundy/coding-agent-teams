import json, sys

def render(e):
    """Render one event as a human-readable line. `ts` is an RFC3339 UTC string, rendered as-is."""
    return f"[{e['id']}] {e['status']} at {e['ts']}"

if __name__ == "__main__":
    print(render(json.load(sys.stdin)))
