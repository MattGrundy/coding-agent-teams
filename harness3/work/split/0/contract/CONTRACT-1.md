# Event wire format (CONTRACT-1)

Producer writes one JSON object to stdout. No trailing newline. No other output.

## Fields

| Field | JSON type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Event id. Unchanged. |
| `ts` | integer | yes | Unix timestamp, seconds. Unchanged. |
| `status` | string | yes | Status. Unchanged. |
| `retry_count` | integer | yes | **New.** Number of times the event was retried before being emitted. Non-negative. `0` = no retries. Not a string, not null. |

## Example

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "retry_count": 3}
```

## Compatibility

- Additive change. Existing fields keep name, type, value semantics.
- Key order in the object: `id`, `ts`, `status`, `retry_count`. Do not depend on order.
- Parsers that reject unknown keys must add `retry_count`.
