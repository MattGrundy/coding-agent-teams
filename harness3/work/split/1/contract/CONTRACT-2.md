# CONTRACT-2: producer event wire format

Supersedes the `ts` definition in CONTRACT-1. All other CONTRACT-1 fields unchanged.

## Transport
- Single JSON object written to stdout, UTF-8, no trailing newline.
- One event per process run.

## Example
```json
{"id": "evt-1", "ts": "2025-06-15T15:06:40Z", "status": "ok", "retry_count": 3}
```

## Fields

| Field | JSON type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Event identifier. Unchanged. |
| `ts` | string | yes | CHANGED. RFC3339 timestamp, UTC. Was integer Unix epoch seconds. Same field name, same instant. |
| `status` | string | yes | Status string, currently `"ok"`. Unchanged. |
| `retry_count` | integer | yes | Retries before emit. Unchanged. |

## `ts` format
- Exact shape: `YYYY-MM-DDTHH:MM:SSZ`, always 20 characters.
- Regex: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`
- Uppercase `T` separator. Uppercase `Z` suffix.
- Always UTC. Never a numeric offset (`+00:00`, `-05:00` are not emitted).
- No fractional seconds. Whole-second precision, same as the old integer.
- Value mapping: old integer `1750000000` == new `"2025-06-15T15:06:40Z"`. Converting the string to Unix seconds yields exactly the old integer.

## Change from previous format
- BREAKING: `ts` JSON type changed from integer to string. Same key name.
- A parser that reads `ts` as a number will fail or misparse. Update it to read a string and parse as RFC3339.
- No other field renamed, removed, retyped, or changed in meaning.
- Key order: `id`, `ts`, `status`, `retry_count`. Not significant in JSON; do not depend on it.

## Consumer requirements
- Parse `ts` as an RFC3339 string. Accepting a general RFC3339 parser is fine; the producer emits only the shape above.
- Do not assume integer `ts`. The producer no longer emits it.
