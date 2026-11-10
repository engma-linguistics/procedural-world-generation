---
id: PW-1578
title: "Languages: since the single sound-change draw, long-lived lines make ~2x more changes per generation than human ones"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lang-weights (PW-1551 lane)
blocked_by: []
relates: [PW-1551]
refs: ["planet/language/lect.py::Lect.step", "planet/language/lect.py::REFIRE_GEN_YR", "planet/language/history.py::RATE_SCALE", "planet/language/checks.py::long_generations", "docs/review/language/calibration.md#pw-1551-lane-2026-11-08-lang-weights-the-draw-without-redraws"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: you ruled that sound change runs per generation, so a dragon people (430-year generations) changes about
15 times more slowly per year than humans. With the new draw (PW-1551) that holds for the number of *chances* a line
gets, but not for the number of changes that happen. A human line now has more chances than it can use: most changes
that could happen have already happened, and the line waits for new material. A dragon line has few chances and uses
nearly all of them. So per generation, dragon lines change about twice as much as human ones, relative to before.

Measured (isolated lines, no contact, own changes per lect-kyr; main / now): humans 14.8 / 17.0, elves 3.9 / 4.7, blue
dragons 1.1 / 2.4. The human-to-dragon ratio fell from 13 to 7. The full-pass check "long generations change less"
(humans over 3x the long-lived per kyr, contact changes included) failed at 2.88 in one pass with the re-fire wait in
years; counting that wait in generations (lect.REFIRE_GEN_YR, in) took dragons from 3.5 to 2.4 in the harness and the
check to 4.84 (stored run 4.36), because contact changes are a large share of the long-lived total.

**What misleads if never done:** dragon and elf languages drift faster per generation than the ruling says, so their
families look shallower than their age (own changes per kyr in the final pass: dragons 2.0, elves 4.2, against 1.7
and 3.8 stored, while their draws per generation equal the humans').

Options:
- A. Accept: per year the long-lived still change 3-4x more slowly than humans, which is what the check asks.
- B. Scale draws per generation by the line's saturation (e.g. draws x the share of the pool that applies), so that
  applied changes, not chances, are per generation. A new mechanism; needs a pass.
- C. Lower RATE_SCALE for all and accept a longer horizon (rate 150 read 16.0 kyr against 11.4).
Lean: A for v1, B if the dragon trees read too shallow.

## Updates
- 2026-11-09: Language wrap-up 11-09: realism polish, parked as later (owner: language good enough to move forward).
- 2026-11-09: Status needs-decision -> todo. Coordinator call (not a trade-off for the owner, 11-09): accept for v1. The 'long generations change less' check passes (4.84); per-generation parity for long-lived lines is a refinement, pick up with PW-1579.
- 2026-11-09: Created from inbox draft draft-language-change-rate-not-linear-in-generations.md (found by lang-weights (PW-1551 lane)).
