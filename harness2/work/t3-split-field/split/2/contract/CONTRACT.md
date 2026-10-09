# Event wire format

Producer writes one JSON object to stdout.

## Sample

```json
{"id": "evt-1", "ts": 1750000000, "status": "ok", "status_reason": "healthy"}
```

## Fields

| Field           | Type    | Meaning                                              |
|-----------------|---------|------------------------------------------------------|
| `id`            | string  | Event id. Unchanged.                                 |
| `ts`            | integer | Unix timestamp, seconds. Unchanged.                  |
| `status`        | string  | The state only. Unchanged name; now carries state and nothing else. |
| `status_reason` | string  | **New.** Why the event is in that state.             |

## What changed

- `status_reason` is a new top-level key, always present, always a string.
- `status` keeps its name and position. In the sample its value is `ok`, the same as before. No consumer that reads only `status` needs to change, provided it tolerates unknown keys.
- Consumers that reject unknown keys (strict schema, `additionalProperties: false`, etc.) must add `status_reason` or they will fail.

## Values

The producer currently emits exactly one combination:

- `status` = `"ok"`, `status_reason` = `"healthy"`

The producer's full sets of `status` and `status_reason` values are not enumerated here, since the current code only emits the one pair above. Treat both fields as open strings: do not fail on an unrecognised value, and do not assume the two fields vary together (for example, do not parse `status_reason` to derive `status`).

## Compatibility

- Additive change. No field renamed, removed or retyped.
- Consumers should read `status` for state and `status_reason` for cause.
- Do not expect `status` to contain the reason (for example `"ok: healthy"`). It never does.
