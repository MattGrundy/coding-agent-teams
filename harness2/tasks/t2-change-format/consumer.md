The event's timestamp is now an RFC3339 string in UTC rather than a unix
integer. Render it as-is, in the same position in the line.

So a line that currently reads `[evt-1] ok at 1750000000` should read
`[evt-1] ok at <the RFC3339 string>`.
