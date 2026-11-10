---
title: "Languages: the 'sisters recognisable' check is one family's story on de1cc6 (229 of 294 pairs); weigh families equally?"
type: task
status: needs-decision
parent: PW-767
subsystem: culture
effort: s
impact: low
found_by: language lane 10 (PW-1615)
blocked_by: []
relates: [PW-1615]
refs: ["planet/language/checks.py::sister_distant", "planet/language/families.py::horizon_from", "planet/language/checks.py::SIBLING_MIN", "run de1cc6", "run a24559", docs/review/language/calibration.md]
---

## Description
In plain words: one check asks whether languages that split up to 2,000 years ago still share enough recognisable
words (over 0.5 on average). On the second world, de1cc6, it reads 0.49 and fails, but 229 of its 294 sister pairs come
from one big family that spread by language shift to half-orcs, humans, halflings and others. So the number mostly
describes that one family's history, not the model.

Lane 10's reading (lane 9's pass output, same code on both worlds):

| | a24559 | de1cc6 |
| --- | --- | --- |
| sister pairs; largest family's share | 165; 56 (34%) | 294; 229 (78%) |
| strict share, pairs parted 0 / 0.5 / 1 / 1.5 / 2 kyr | .81 / .72 / .54 / .52 / .44 | .85 / .67 / .51 / .45 / .36 |
| pairs parted 1.5-2 kyr | 90 of 165 | 180 of 294 |
| de1cc6 re-weighted to a24559's age mix | | 0.53 |

So most of the gap is the age mix (a burst of splits 1.5-2 kyr ago in one family); the rest is that family's
shift-heavy history (its true cognate share at 2 kyr is 0.44 against a24559's 0.58).

Options:
- **A. Leave the check as is.** de1cc6 counts as an outlier world for this check (the multi-seed bar is ~70%).
- **B. Weigh families equally:** the check's value is the mean over families of each family's mean sister share
  (the pair mean shown beside it). One family can no longer set the number; small families get noisier.
- **C. Standardise the age mix:** average the per-bin shares (0, 0.5, 1, 1.5, 2 kyr) with fixed weights.

Lean: A for now; B if a third world fails the same way. B and C change what the check measures, so they are a call for
the owner, not a lane.

**What misleads if never done:** a lane running a second seed reads a sisters failure as its own regression when it is
one family's history.
