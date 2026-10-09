# Measuring Whether Any of It Worked

*Part 2 of a series on running a team of coding agents. Each part stands alone.*

I ran an agent team for months and formed opinions about it. Opinions are cheap, so I
built a scored harness to check two of them.

The first opinion did not survive. The second could not be tested by the experiment I
built for it, and it took three attempts to work out why. Both of those are more useful
than the numbers I set out to collect, so this is an account of measuring something
badly, several times, until the measurement itself became the finding.

Everything here is reproducible: the cases, the runners and every superseded version
are in the repository beside this piece.

### The setup

Twelve small Go diffs. Eight carry a planted defect: a spec violation, a missed call
site, a swallowed error, a nil dereference, a substring match where parsing is needed,
an over-abstraction, scope creep, and one special case I will come back to. Four are
clean, and two of those are bait: one is scope creep the task explicitly asked for,
the other is an unusual-looking approach that happens to be correct. The bait exists
so that a reviewer which blocks everything scores badly rather than well.

Two reviewers see each diff three times. The verdict is the majority.

The special case is the one worth describing. The task says: the guard denies when it
cannot parse a command, this produces false denials that block real work, make it stop
doing that. The diff does exactly that, turning an unparseable command into an allow.
It is a security regression, and the task asked for it.

### Version one

I wrote both briefs myself and gave them a binary pass/block with no severity bar.

The first reviewer blocked four clean diffs out of four. The gate blocked eleven of
twelve cases. Its catch rate on defects was 7/8, which means nothing at all, because
a reviewer that always blocks catches every defect by construction.

Only one diff got through, so the headline metric I had built the whole thing for was
computed over a single case.

### Version two

I added an explicit bar: block only for a nameable defect, say what breaks and on what
input, style and naming are notes rather than blocks, most diffs are fine.

That helped. False blocks fell from four to three. And it produced a result that looked
publishable:

Both reviewers caught the same seven defects. Both missed the same one, the fail-open
the task had requested. Neither caught anything the other missed, in any case, at all.
That is the redundancy claim in its strongest form, and I believed it.

### Version three

Then I checked my briefs against the real ones, and they did not match.

I had written both reviewers as variants of "is this a good change", differing in angle.
The actual split is sharper. One reviewer reads line by line for logic, edge cases,
security and idiom, and is explicitly told that proportionality, duplication and scope
are somebody else's problem. The other reads the diff against the stated goal, and is
told that a change weakening a safety property is blocking even when the task asked for
it, because the task being wrong does not make the diff right.

With those briefs, both reviewers caught eight of eight. Including the fail-open.

The version two finding evaporated. It had been a property of my writing, not of the
reviewers.

| | v1 (no bar) | v2 (bar added) | v3 (real briefs) |
| --- | --- | --- | --- |
| Defects caught, reviewer A | 7/8 | 7/8 | 8/8 |
| Defects caught, reviewer B | 6/8 | 7/8 | 8/8 |
| False blocks on clean, A | 4/4 | 3/4 | 1/4 |
| False blocks on clean, B | 1/4 | 1/4 | 2/4 |
| The requested fail-open | missed | missed | caught |

One number moved the wrong way. The critique reviewer's false blocks went from one in
four to two in four, so the briefs that made it catch more also made it refuse more. On
a set this small that is a single case, and I have no account of why it happened, but it
is the only figure in the table that got worse and it would be convenient to skip past.

### What this actually showed

Not what I set out to measure. The largest effect in the whole experiment was how the
reviewers were specified. Same model, same diffs, same harness, three runs each. The
only thing that changed was the wording of two briefs, and it moved the hardest case
from missed twice to caught.

That is worth more than the number I was chasing. It says the reviewer gate's value
lives almost entirely in the definitions, and that two reviewers who are nominally
different but actually asking the same question will agree with each other and tell you
nothing. Which is a real version of the redundancy worry, just not the one I had.

It also means I still cannot answer the question I started with. In version three both
lenses caught everything, so the second lens measured zero marginal value for the
second time, now because nothing in the set was hard enough to separate them. A ceiling
is not a result. To learn whether the second reviewer earns its cost I would need
defects that one lens can see and the other genuinely cannot, and building those
honestly is harder than building the harness was.

### The second question: does splitting across projects pay?

The other claim worth testing was about boundaries. Same coordinated change, made two
ways: one session holding both repositories, versus two sessions that never see each
other's code and agree a wire format through a written contract. The integration check
fails unless both sides land on the same field name, which I deliberately left
unspecified, so a coordination failure shows up as a test failure rather than as a
judgement call.

I ran it twice, because the first version was the wrong experiment.

**The naive test.** Cold sessions, one task each, measured per task.

| | one session | two sessions + contract |
| --- | --- | --- |
| Integration passed | 9/9 | 9/9 |
| Median cost | $0.092 | $0.198 |
| Peak context in any one session | 35,043 | 35,896 |

Splitting cost 2.16x and bought nothing measurable. But peak context is identical
across both regimes, and that is the tell. Roughly 35,000 tokens is what a session
costs before it does anything at all: system prompt, tool definitions, the fixed floor.
My tasks were too small to grow a context past it. Two sessions pay that floor twice,
so split loses two to one by construction, whatever the architecture is worth.

**The simulated real test.** So I ran the regime the claim is actually about: long-lived
sessions working a sequence of coordinated changes, each landing on top of the last,
with the check re-run cumulatively so task two must not break task one. Sessions
persist across the sequence rather than starting cold.

| | task 1 | task 2 | task 3 | sequence total |
| --- | --- | --- | --- | --- |
| One session, cost | $0.094 | $0.124 | $0.152 | $0.37 |
| Two sessions, cost | $0.195 | $0.282 | $0.354 | $0.83 |
| One session, peak context | 34,799 | 36,148 | 37,378 | |
| Two sessions, peak context | 35,446 | 38,052 | 40,177 | |

Twelve runs, twelve passes, no contract drift in either direction. And no crossover.
Split stayed about 2.3x throughout, and its context grew faster rather than slower,
because two sessions each accumulate their own history and the contract notes pile up
alongside.

### What the artefacts showed that the numbers did not

Then I read what the runs actually produced, which I should have done first.

The final code is essentially identical between regimes. Both converged on the same
consumer; the producers differ only in whether a conversion is inlined or given a name.

The difference is what else exists afterwards. The split runs left behind three
versioned interface specifications. The second one pins a timestamp format to a regex,
states the offset is always a literal `Z` and never `+00:00`, rules out fractional
seconds, fixes the case of the letters, and gives the mapping from the old integer
form. The third marks a field removed, maps the old value onto the new pair, and warns
the reader not to parse one field out of the other or reject values it has not seen.
Forty-odd lines of specification for a one-field change, written because the author
could assume nothing about who would read it.

The single-session runs left behind the diff and nothing else.

My scoring gave that difference a value of zero. I measured cost and correctness, and
a written contract is neither. Which is awkward, because [part 1](01-running-a-team-of-coding-agents.md)
argues that records outliving the session are the point of the whole architecture, and
then I built an experiment that treats producing one as pure overhead.

It does not rescue the cost ratio. But "2.3x more expensive, same code, plus a
specification you could hand to a third team next year" is a different claim from "2.3x
more expensive", and I would have published the second one.

### Why neither test settles it

Both experiments say splitting costs more. My own experience, and that of the person
who has run this setup across real repositories, says the opposite. The fixture
explains the gap.

The two services in my fixture couple through a single JSON object with five fields.
That is the entire surface. Neither side ever needed the other's implementation
details, because there are barely any to need. So the boundary excludes almost nothing,
while the contract costs full price.

Real projects do not couple like that. They couple through shared conventions, error
semantics, assumptions about retries and ordering, helpers each side expects the other
to honour, and a hundred small things nobody wrote down. Carrying a second project
means carrying all of that, and it is exactly the mass a boundary excludes.

So the variable that decides this is not task count, and not session lifetime, both of
which I varied. It is the size of the coupling surface, which I held near zero. On a
fixture with one narrow explicit contract, splitting is overhead. The crossover lives
somewhere out in fixtures I have not built.

I could go and build them. I would want to declare the sweep before running it, because
the temptation to enlarge the fixture until the answer comes out right is obvious, and
an experiment tuned until it agrees with you is not evidence.

### The part that rhymes

[Part 1](01-running-a-team-of-coding-agents.md) closes on the claim that agent systems
generate a great deal of plausible evidence that things are fine, and that the
engineering problem is building the few things that produce evidence you can rely on.

Then I built an evaluation that produced a clean, quotable, completely false result,
and I believed it until I checked an assumption I had not thought to question. The
thing that caught it was the same thing that catches an unwired guard: looking at the
column where nothing should happen. A reviewer blocking four clean diffs out of four is
the same signal as a guard that never fires. Both look like they are working.

### Running it yourself

The cases, the runners, the scoring and every superseded version of the briefs and their
results are in the repository beside this piece. The three harnesses are the reviewer
gate eval, the naive cross-project test, and the persistent-session one. Each runs with
`python3 gen_cases.py && python3 run.py && python3 score.py`.

What none of it measures, plainly. Both reviewers are the same model wearing two hats,
which is the arrangement under criticism, so this cannot tell you what genuinely
independent reviewers would do. Twelve cases means a difference of one or two is noise.
And the defects were planted by the same person who wrote the briefs and did the
scoring, on diffs alone, not a working tree the reviewers could build and test against.

If you point it at your own reviewer definitions, I would expect the version-three
result to be the fragile one. It depends entirely on how well the two briefs are
separated, and that is the finding.
