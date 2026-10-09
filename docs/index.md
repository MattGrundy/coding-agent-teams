# Running a Team of Coding Agents

Notes from building and running a lead-and-specialists agent architecture on real
work: what the shape was, which decisions held up, where it broke, and what happened
when I tried to measure any of it.

Each part stands on its own. They share a subject, not a plot.

| | Part | Thesis |
| --- | --- | --- |
| 1 | [Running a team of coding agents](01-running-a-team-of-coding-agents.md) | Coordination state that lives only in a context window is not coordination |
| 2 | [Measuring whether any of it worked](02-measuring-whether-it-worked.md) | The reviewer briefs mattered more than the architecture, and my first clean result was an artefact of my own writing |
| 3 | [Controls that aren't controls](03-controls-that-arent-controls.md) | Guards that live in a settings file on my machine were never controls at all on anyone else's |

More parts are planned — bounded autonomy, and working across projects — and will
appear here when they're written.

## The evidence

Part 2's numbers come from harnesses in the repository behind this site. Every
superseded version of the reviewer briefs and their results is kept, because the
progression is the point.

- [`harness/`](https://github.com/MattGrundy/coding-agent-teams/tree/main/harness) —
  reviewer gate eval. 12 Go diffs, 8 with a planted defect and 4 clean, two of the
  clean ones designed as bait so that a reviewer which blocks everything scores badly
  rather than well. Three versions of the briefs and their results.
- [`harness2/`](https://github.com/MattGrundy/coding-agent-teams/tree/main/harness2) —
  cross-project eval, cold sessions, one task each.
- [`harness3/`](https://github.com/MattGrundy/coding-agent-teams/tree/main/harness3) —
  cross-project eval, persistent sessions, three sequential tasks with a cumulative
  integration check.

[`harness/README.md`](https://github.com/MattGrundy/coding-agent-teams/blob/main/harness/README.md)
has the method and, more usefully, what it does not measure.

## What this is not

One model wearing two hats, twelve cases, and defects planted by the same person who
wrote the reviewer briefs and the scoring. Reviewers saw a diff and a snippet, not a
working tree they could build or test. Read the numbers as an order of magnitude. The
finding that survives is about how much the definitions matter, not about any
particular score.

## Licence

The prose is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — quote and
republish it freely with attribution. The harness code is MIT.
