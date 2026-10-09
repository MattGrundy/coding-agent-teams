# Event wire format

Producer writes one JSON object to stdout.

## Sample

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "status_reason": "healthy"}
```

## Fields

| Field           | Type    | Meaning                                   | Sample value   |
|-----------------|---------|-------------------------------------------|----------------|
| `id`            | string  | Event id. Unchanged.                      | `"evt-1"`      |
| `ts`            | integer | Unix timestamp, seconds. Unchanged.       | `1750000000`   |
| `status`        | string  | The state only. Unchanged name and type.  | `"ok"`         |
| `status_reason` | string  | **NEW.** Why the event is in that state.  | `"healthy"`    |

## What changed

- New field `status_reason` (string, always present) carries the reason.
- `status` keeps its name and type and now holds the state only. Sample: `"ok"`.
  No reason text is put in `status`.
- No field was renamed or removed. Parsers that ignore unknown keys keep working
  unchanged. Parsers that reject unknown keys (strict schema) must add
  `status_reason` before deploying against this producer.

## Values

Only the pair emitted today is guaranteed: `status = "ok"`, `status_reason = "healthy"`.
The full sets of possible `status` and `status_reason` values are not enumerated by
this contract. Treat both as open-ended strings; do not hard-fail on unknown values.
`status_reason` values are not guaranteed to be valid only for one particular `status`.

## Parsing guidance

- Read the state from `status`, the reason from `status_reason`.
- Do not parse or split `status` to derive a reason.
- Key order is not significant.
