# Event wire format

Producer writes one JSON object to stdout, no trailing newline.

## Example

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "retry_count": 3}
```

## Fields

| Field         | JSON type | Description                                          | Change    |
|---------------|-----------|------------------------------------------------------|-----------|
| `id`          | string    | Event identifier                                     | unchanged |
| `ts`          | integer   | Timestamp, Unix epoch (as emitted: 1750000000)       | unchanged |
| `status`      | string    | Status (as emitted: `"ok"`)                          | unchanged |
| `retry_count` | integer   | Number of times the event was retried before emission | **NEW**   |

## `retry_count`

- Key name exactly `retry_count` (lowercase, underscore).
- JSON number, integer, no quotes, no fraction. Non-negative; 0 means no retries.
- Always present in every emitted event, never null.
- Sample event value: `3`.

## Compatibility

- Purely additive: existing fields keep name, type and meaning.
- Consumers that reject unknown keys (strict schema, `additionalProperties: false`, strict deserializers) must be updated to accept `retry_count` before this producer version is deployed.
- Consumers that ignore unknown keys need no change unless they want the value.
- Key order in the object is not significant.
