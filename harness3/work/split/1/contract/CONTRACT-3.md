# CONTRACT-3: producer event wire format

Supersedes the `status` definition in CONTRACT-1/2. All other fields unchanged (`ts` as in CONTRACT-2).

## Transport
- Single JSON object written to stdout, UTF-8, no trailing newline.
- One event per process run.

## Example
```json
{"id": "evt-1", "ts": "2025-06-15T15:06:40Z", "status": "ok", "status_reason": "healthy", "retry_count": 3}
```

## Fields

| Field | JSON type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Event identifier. Unchanged. |
| `ts` | string | yes | RFC3339 UTC, `YYYY-MM-DDTHH:MM:SSZ`. Unchanged from CONTRACT-2. |
| `status` | string | yes | State only. Same key as before. Sample: `"ok"`. |
| `status_reason` | string | yes | NEW. Why the event is in the state given by `status`. Sample: `"healthy"`. |
| `retry_count` | integer | yes | Retries before emit. Unchanged. |

## Change from previous format
- Added top-level key `status_reason` (string).
- `status` keeps its key and type; it now carries the state alone. The reason is no longer folded into it.
- Only the pair (`status` = `"ok"`, `status_reason` = `"healthy"`) is emitted today. No other values are emitted at present, but do not hard-code that set: treat both as open strings and tolerate unknown values.
- `status_reason` is always present and never null. Its meaning is scoped to `status`; do not interpret it alone.
- No other field renamed, removed, retyped, or changed in meaning.
- Key order: `id`, `ts`, `status`, `status_reason`, `retry_count`. Not significant in JSON; do not depend on it.

## Consumer requirements
- Read state from `status`, reason from `status_reason`.
- Parsers that reject unknown keys must be updated to allow `status_reason`.
- Do not parse `status` for a combined "state:reason" form. It is never combined.
