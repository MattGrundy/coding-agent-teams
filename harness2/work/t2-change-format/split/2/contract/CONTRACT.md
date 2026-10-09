# Event wire format

The producer writes one JSON object to stdout.

## Example

```json
{"id": "evt-1", "ts": "2025-06-15T15:06:40Z", "status": "ok"}
```

## Fields

| Field    | JSON type | Description |
|----------|-----------|-------------|
| `id`     | string    | Event id. Unchanged. |
| `ts`     | string    | Event time. **CHANGED** (see below). |
| `status` | string    | Unchanged. |

## Breaking change: `ts`

- Before: JSON integer, unix seconds since epoch (e.g. `1750000000`).
- Now: JSON **string**, RFC3339 timestamp in UTC (e.g. `"2025-06-15T15:06:40Z"`).
- Field name is unchanged (`ts`). Only its type and format changed.
- Same instant: `1750000000` == `"2025-06-15T15:06:40Z"`.

### Exact format

Always `YYYY-MM-DDTHH:MM:SSZ`, matching `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`:

- Date and time separated by uppercase `T`.
- Offset is always the literal uppercase `Z` (UTC). Never `+00:00`, never any other offset.
- Whole seconds only. No fractional seconds.
- Four-digit year, zero-padded fields.

### Consumer action

A parser that reads `ts` as an integer will fail on this value. Parse it as an RFC3339 / ISO 8601 UTC datetime string. To get unix seconds, convert the parsed instant to epoch seconds.
