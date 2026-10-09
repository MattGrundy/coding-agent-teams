# consumer

Reads one JSON event on stdin and prints a human-readable line.
The wire format is produced by another service, maintained by another team.

`ts` is an RFC3339 UTC string (`YYYY-MM-DDTHH:MM:SSZ`), rendered as-is:
`[evt-1] ok at 2025-06-15T15:06:40Z`.
