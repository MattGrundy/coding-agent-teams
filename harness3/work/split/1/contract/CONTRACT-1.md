# CONTRACT-1: producer event wire format

## Transport
- Single JSON object written to stdout, UTF-8, no trailing newline.
- One event per process run.

## Example
```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "retry_count": 3}
```

## Fields

| Field | JSON type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Event identifier. Unchanged. |
| `ts` | integer | yes | Unix epoch seconds. Unchanged. |
| `status` | string | yes | Status string, currently `"ok"`. Unchanged. |
| `retry_count` | integer | yes | NEW. Number of times the event was retried before being emitted. `0` = emitted on first attempt. Never null, never negative, never a string. Sample value: `3`. |

## Change from previous format
- Added top-level key `retry_count`.
- No existing field renamed, removed, retyped, or changed in meaning.
- Key order in the object: `id`, `ts`, `status`, `retry_count`. Order is not significant in JSON; do not depend on it.

## Consumer requirements
- Parser must accept `retry_count` as an integer.
- Parsers that reject unknown keys must be updated to allow `retry_count`.
- Parsers may treat `retry_count` as required: the producer always emits it.
