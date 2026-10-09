# Producer event wire format

Producer writes one JSON object to stdout (UTF-8, no trailing newline).

## Sample

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "retry_count": 3}
```

## Fields

| Field         | JSON type | Description                                              |
|---------------|-----------|----------------------------------------------------------|
| `id`          | string    | Event identifier, e.g. `"evt-1"`.                        |
| `ts`          | integer   | Unix timestamp in seconds, e.g. `1750000000`.            |
| `status`      | string    | Status, e.g. `"ok"`.                                     |
| `retry_count` | integer   | **NEW.** Number of times the event was retried before it was emitted. |

## `retry_count` details

- Name: exactly `retry_count` (snake_case, case-sensitive).
- Type: JSON number, integer (no decimal point, no quotes). Sample value: `3`.
- Meaning: retries before emission. First-attempt success means `0`. It does not count the initial attempt.
- Range: non-negative integer.
- Always present in every event. Never `null`, never omitted.

## Compatibility

- Additive change only. `id`, `ts`, `status` are unchanged in name, type and meaning.
- Consumers that reject unknown fields must be updated to accept `retry_count`.
- Consumers that ignore unknown fields need no change unless they want to use the value.
- Key order in the object is not significant and must not be relied on.
