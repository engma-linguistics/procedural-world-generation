---
id: PW-937
title: Scale every people's patch viable number by its generation time, not only the megafauna's
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-37
blocked_by: []
relates: [PW-924, PW-888, PW-931]
refs: [planet/lineages/history/dispersal.py, planet/lineages/history/origins.py, planet/lineages/samples/dnd.toml]
created: 2026-10-27
updated: 2026-10-28
---

## Description
PW-924 added `History.line_mvp`: the viable number of a separate patch (`_viable`, the fade of small patches) is
`tree.viable_pop x (25 / generation_yr)^(1/PERSIST_EXP)`. Over the same span in years a long-lived line lives fewer generations, so it
needs fewer individuals to persist (Lande 1993, the same rule `origin_mvp` already uses for founders). It is applied only to megafauna
lines (dragons at 200 yr need 62, giants at 65 yr ~190), so the peoples' behaviour is unchanged.

The rule is general. Applied to every people, the long-lived ones (elves 50 yr, dwarves and gnomes 40 yr) would keep smaller separate
patches (gnomes need 312 instead of 500), which may help the PW-931 gnome remnants. Short-lived peoples (goblins at 15 yr) would stay at
500 (the scale is capped at 1, so it never raises the number).

Options:
- A: apply to all peoples (drop the megafauna guard in `line_mvp`), re-run the 6 x 4 peoples sweep.
- B: keep it megafauna-only (as merged).

Lean: A, since it is the same mechanism as the founder rule, but it shifts every long-lived people's ranges, so it needs the sweep and the owner's yes.
- [ ] decision recorded; if A, the 6 x 4 sweep compared before and after

## Updates
- 2026-10-28: Status needs-decision -> done. Merged 94c5a318 (neutral, 18 remnants as main).
- 2026-10-28: 10-28: dragons' own generation time is short (200 yr vs ~430 yr from the approved age structure; inbox draft-megafauna-3). Decide this one with that in mind.
- 2026-10-27: Created from inbox draft draft-viable-pop-by-generation-for-all-peoples.md (found by fun-lane-37).
