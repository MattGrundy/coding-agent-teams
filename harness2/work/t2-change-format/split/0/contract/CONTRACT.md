# Event wire format

Producer writes one JSON object to stdout.

## Breaking change: `ts` type

`ts` was a JSON integer (unix seconds). It is now a JSON **string**, RFC3339 in UTC.
Field name is unchanged (`ts`). Same instant is represented.

| field    | type   | notes                                   |
|----------|--------|-----------------------------------------|
| `id`     | string | unchanged                               |
| `ts`     | string | **changed** — was integer unix seconds  |
| `status` | string | unchanged                               |

## `ts` format

- Exact pattern: `YYYY-MM-DDTHH:MM:SSZ`
- Always UTC, always the literal suffix `Z` (never `+00:00` or another offset).
- Always 4-digit year, zero-padded fields, uppercase `T` and `Z`.
- Whole-second precision, no fractional seconds. (Old integer was whole seconds, so nothing is lost.)
- Regex: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`

Example, before and after (same instant):

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok"}
{"id": "evt-1", "ts": "2025-06-15T15:06:40Z", "status": "ok"}
```

## Consumer action

Parse `ts` as an RFC3339 string instead of an integer. A parser that expects a number will
fail or misread the string. To recover the old value, convert the parsed instant to unix seconds.
