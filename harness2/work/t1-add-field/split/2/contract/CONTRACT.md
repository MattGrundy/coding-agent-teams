# Producer event wire format

Emitted by `producer/emit.py` on stdout as a single JSON object (UTF-8, no trailing newline, Python `json.dump` default formatting: `", "` and `": "` separators).

## Example

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "retry_count": 3}
```

## Fields

| Field         | JSON type | Description                                                          |
|---------------|-----------|----------------------------------------------------------------------|
| `id`          | string    | Event identifier. Unchanged.                                         |
| `ts`          | integer   | Unix timestamp in seconds. Unchanged.                                |
| `status`      | string    | Status, e.g. `"ok"`. Unchanged.                                      |
| `retry_count` | integer   | **New.** Number of times the event was retried before being emitted. |

## `retry_count`

- Always present in every event; never `null`.
- Non-negative integer. `0` means emitted on first attempt, without any retry. The sample event has `3`.
- Counts retries only, not total attempts (attempts = `retry_count + 1`).
- Plain JSON number, no quotes, no fractional part.

## Compatibility

- Change is additive: the three existing fields keep the same names, types and meaning.
- Consumers that reject unknown keys (strict schema / `additionalProperties: false` / strict deserializers) must be updated to accept `retry_count` **before** this producer version is deployed.
- Consumers that ignore unknown keys need no change, but should add the field to read the value.
- Do not depend on key order.
