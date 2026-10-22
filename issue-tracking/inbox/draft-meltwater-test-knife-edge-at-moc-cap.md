---
title: test_meltwater_weakens_the_overturning sits on a knife edge at the overturning's moc_k cap
type: task
status: needs-decision
parent: null
subsystem: ocean
effort: s
impact: med
found_by: laneA4 (PW-578 attempt 2)
blocked_by: []
relates: [PW-578, PW-458]
refs: [tests/test_ocean.py, planet/ocean.py, docs/review/base-climate/stages.md]
---

## Description
In the two-basin fixture (`tests/test_ocean.py::basins`, L4) the northern overturning is held at its cap
(`ocean.overturning`: each sea's cell carries at most `moc_k` × its sinking-weighted density difference). A
meltwater pulse over the main site moves its sinking to the other northern cells, as the test expects (the near
sinking falls from 4.4 to 0.06 Sv). But the northern total is the cap both times. Freshening takes the site's
lighter cells out of the weighting, so the weighted density difference, and with it the cap, can go *up* a little.

PW-578 attempt 2 (the sea's own swing from the mixed layer, plus stable summer land air) gives 20.1342 → 20.1353 Sv
(+0.005%), and the test's `<= s[north].sum() + 1e-9` fails. Small perturbations of the sea's swing flip the sign:

| variant | north before → after melt (Sv) |
|---|---|
| attempt 2 | 20.1342 → 20.1353 (fails) |
| F1 own swing (3 C flat) | 20.0067 → 19.9146 |
| own + 0.5 C | 20.1428 → 20.0785 |
| own − 0.3 × s | 20.1227 → 20.1562 (fails) |

So the line tests a tie, not a mechanism. Options:
- A: the cap uses a density difference the meltwater can only lower, e.g. the deep water's `ref` against the inflow,
  rather than the sinking-weighted mean. That is physically closer to Stommel's box, but it is an ocean change
  (stage 1's code).
- B: the coordinator rules that the test's third line may compare with a tolerance (a change to the test, which the
  PW-578 rules forbid without a ruling).
- C: leave it, and pick PW-578 variants that happen to pass. That is test-fitting.

Lean: A.
