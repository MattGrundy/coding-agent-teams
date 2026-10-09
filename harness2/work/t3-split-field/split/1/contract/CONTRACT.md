# Event wire format

Producer writes one JSON object to stdout.

## Sample

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "status_reason": "healthy"}
```

## Fields

| Field           | Type    | Description |
|-----------------|---------|-------------|
| `id`            | string  | Event id. Unchanged. |
| `ts`            | integer | Unix timestamp, seconds. Unchanged. |
| `status`        | string  | The state only. Name, type and meaning unchanged. Sample value: `ok`. |
| `status_reason` | string  | **NEW.** Why the event is in that state. Sample value: `healthy`. |

## What changed

- Added one field: `status_reason` (string, always present in emitted events).
- `status` is not renamed or removed. It carries the state only (`ok`), as before.
  The reason lives in `status_reason`, not in `status`.
- No other fields changed.

## Compatibility

- Additive change. A parser that ignores unknown keys keeps working with no change.
- A parser that rejects unknown keys (strict schema) must add `status_reason: string`.
- To use the reason, read `status_reason`. Do not derive it from `status`.

## Known values

Only the pair seen in the sample is defined here: `status="ok"`, `status_reason="healthy"`.
The producer does not currently emit any other state/reason combinations, and no
enumeration of possible values is promised. Treat both fields as open strings and
handle unrecognized values gracefully.
