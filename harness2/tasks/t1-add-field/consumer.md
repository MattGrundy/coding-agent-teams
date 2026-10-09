The event now carries a retry count. Append it to the rendered line as
` retries: N` (a single leading space, then the literal `retries: `, then the number).

So a line that currently reads `[evt-1] ok at 1750000000` should read
`[evt-1] ok at 1750000000 retries: 3`.
