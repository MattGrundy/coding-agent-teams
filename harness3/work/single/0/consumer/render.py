import json, sys

def render(e):
    """Render one event as a human-readable line."""
    return f"[{e['id']}] {e['state']} ({e['reason']}) at {e['ts']} retries: {e['retry_count']}"

if __name__ == "__main__":
    print(render(json.load(sys.stdin)))
