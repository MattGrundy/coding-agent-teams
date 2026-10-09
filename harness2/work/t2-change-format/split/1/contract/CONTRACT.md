# Event wire format

Producer writes one JSON object to stdout (UTF-8).

## Breaking change: `ts`

The field name is unchanged (`ts`), but its **type and value format changed**.

| | Before | Now |
|---|---|---|
| JSON type | number (integer) | **string** |
| Value | unix seconds, e.g. `1750000000` | RFC 3339 UTC timestamp, e.g. `"2025-06-15T15:06:40Z"` |

Same instant: `1750000000` (old) == `"2025-06-15T15:06:40Z"` (new).

### Exact `ts` format

Always matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`, i.e. `YYYY-MM-DDTHH:MM:SSZ`:

- Timezone is always UTC, written as the literal suffix `Z`. Never a numeric offset (`+00:00`), never a local time.
- Whole seconds only. No fractional seconds.
- Uppercase `T` separator, uppercase `Z`.
- Zero-padded fields, 4-digit year.
- `ts` is never null and never a number.

Consumers must parse it as an RFC 3339 / ISO 8601 UTC datetime string, not as an integer. A parser that expects an integer will fail on this event.

## Full event example

```json
{"id": "evt-1", "ts": "2025-06-15T15:06:40Z", "status": "ok"}
```

## Unchanged fields

- `id`: string
- `status`: string
