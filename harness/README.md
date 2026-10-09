# Reviewer gate eval

Measures one claim from the essay: **when both reviewers pass a diff, how often was
there actually a defect?**

## Method

12 Go diffs, 8 with a planted defect, 4 clean. Each case carries the task the author
was supposedly given, the diff, and sometimes surrounding code. Ground truth lives
in `truth.json` next to each case.

Two reviewers, briefed as the essay describes them:

- **A** asks "does this do what the task said, correctly?"
- **B** asks "should this have been done this way at all?"

Each reviewer sees each case 3 times. The verdict for a pair is the majority across
those runs; the spread is reported as instability.

```
python3 gen_cases.py                          # materialise cases/
python3 run.py --model sonnet --runs 3        # -> results/runs.jsonl
python3 score.py                              # metrics
```

## Defect classes

Chosen so they are not all aimed at one reviewer:

| Case | Class | Who should catch it |
| --- | --- | --- |
| 01 | Spec violation (ttl=0 prunes everything) | A |
| 02 | Missed call site | A |
| 03 | Fail-open, explicitly requested by the task | B (A should pass it) |
| 04 | Swallowed error | A |
| 05 | Wrong abstraction | B |
| 06 | Scope creep | B |
| 07 | Nil deref on a map of pointers | A |
| 08 | Substring match where parsing is needed | A or B |
| 09-12 | Clean | neither |

Case 03 is the interesting one. The task asks for the regression, so a reviewer
checking only "did it do what was asked" should pass it. If the split works, B
catches it alone.

Two of the clean cases are bait. Case 10 is scope creep the task explicitly
requested. Case 11 is an unusual-looking approach that is correct. Both exist so
that a reviewer which blocks everything scores badly rather than well.

## What this does not measure

- **One model.** Both reviewers are the same model with different briefs, which is
  the setup being criticised. It cannot tell you what genuinely independent
  reviewers would do.
- **Small n.** 12 cases. Differences of one or two cases are noise.
- **Planted defects.** Written by the same person who wrote the briefs and the
  scoring, already believing the conclusion. Real defects are messier and rarely
  sit alone in a 15-line diff.
- **No repo.** Reviewers see a diff and a snippet, not a working tree they can
  build or test. That disadvantages the missed-call-site class in particular.

Read the numbers as an order of magnitude, not a measurement.
