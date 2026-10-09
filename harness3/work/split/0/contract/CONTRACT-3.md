# Event wire format (CONTRACT-3)

Producer writes one JSON object to stdout. No trailing newline. No other output.

Supersedes the `status` definition in CONTRACT-1 and CONTRACT-2. Breaking change: `status` removed, replaced by `state` and `reason`.

## Fields

| Field | JSON type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Event id. Unchanged. |
| `ts` | string | yes | RFC 3339 UTC timestamp, `YYYY-MM-DDTHH:MM:SSZ`. Unchanged from CONTRACT-2. |
| `state` | string | yes | **New.** The state. Takes the role of the old `status` value. Sample value: `ok`. |
| `reason` | string | yes | **New.** Why the event is in that state. Sample value: `healthy`. |
| `retry_count` | integer | yes | Unchanged from CONTRACT-1. Non-negative. |
| ~~`status`~~ | | | **Removed.** Not emitted. |

## Mapping from old `status`

- Old `status: "ok"` is now `state: "ok"` with `reason: "healthy"`.
- `state` and `reason` are independent strings. Do not concatenate or parse one from the other.
- Only the pair `state: "ok"`, `reason: "healthy"` is emitted by the current producer. Treat both as open string sets: do not reject unknown values.

## Example

```json
{"id": "evt-1", "ts": "2025-06-15T15:06:40Z", "state": "ok", "reason": "healthy", "retry_count": 3}
```

## Compatibility

- Parser reading `status` finds no such key. Must read `state` (and `reason`).
- Other fields: no change.
- Key order in the object: `id`, `ts`, `state`, `reason`, `retry_count`. Do not depend on order.
