# Running a Team of Coding Agents

Notes from building and running a lead-and-specialists agent architecture on real
work: what the shape was, which decisions held up, where it broke, and what happened
when I tried to measure any of it.

Each part stands on its own. They share a subject, not a plot.

## In short

If you read nothing else: **almost every failure in here was something that looked like a
control and wasn't.** An instruction that was really a suggestion. A guard that was really
unwired. A default that was really someone else's config. A clean 2/2 that was really one
opinion counted twice. Agent systems generate a great deal of plausible evidence that
things are fine, and the engineering problem is building the few things that produce
evidence you can rely on — then being clear-eyed about which is which.

The three parts, in one line each:

1. **The architecture that held** was a coordinator that never writes code, work recorded
   on disk rather than in a conversation, and policy enforced where intent becomes effect.
   The most expensive bug class was none of those: it was guards resolving policy from
   where the session happened to be rather than from what the command targeted.
2. **The measurement mattered more than the architecture.** The reviewer briefs dominated
   the result, and my first clean, quotable number was an artefact of how I had written
   them. What caught it was looking at the column where nothing should have happened.
3. **Guards on my machine were never controls on anyone else's.** Client-side enforcement
   is advisory, opt-in and absent where it isn't installed. Only the forge holds, and it
   is an afternoon of work.

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
