# Event wire format (CONTRACT-2)

Producer writes one JSON object to stdout. No trailing newline. No other output.

Supersedes the `ts` definition in CONTRACT-1. Breaking change: `ts` type changed.

## Fields

| Field | JSON type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Event id. Unchanged. |
| `ts` | string | yes | **Changed.** Event time as RFC 3339 timestamp, always UTC. Was integer unix seconds. Same field name. |
| `status` | string | yes | Status. Unchanged. |
| `retry_count` | integer | yes | Unchanged from CONTRACT-1. Non-negative. |

## `ts` format

- Exact pattern: `YYYY-MM-DDTHH:MM:SSZ`
- Regex: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`
- Offset is always the literal `Z`. Never `+00:00`, never another offset.
- No fractional seconds. Second precision (same as old integer).
- Uppercase `T` and `Z`.
- Same instant as old value: old integer N maps to the UTC time N seconds after 1970-01-01T00:00:00Z.
- Any RFC 3339 parser accepts it.

## Example

```json
{"id": "evt-1", "ts": "2025-06-15T15:06:40Z", "status": "ok", "retry_count": 3}
```

(`ts` was `1750000000`.)

## Compatibility

- Parser that reads `ts` as integer breaks. Must read string and parse RFC 3339.
- Other fields: no change.
- Key order in the object: `id`, `ts`, `status`, `retry_count`. Do not depend on order.
