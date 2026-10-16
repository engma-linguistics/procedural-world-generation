---
id: PW-275
title: "Ice: a new cap starts under a stricter rule in the run (no snow damping) than in the time zoom (LOCAL floor)"
type: task
status: done
parent: PW-245
subsystem: timezoom
effort: s
impact: med
found_by: audit-ice-veg
blocked_by: []
relates: [PW-240, PW-033]
refs: [planet/tectonics/earth.py, planet/timezoom.py, planet/icemass.py, docs/review/audit/ice-veg.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The two sides test whether bare ground starts a cap in different ways:
- The run (earth.py:260) calls `icemass.balance(h=0, cover=0)`: lying seasonal snow gets no summer damping.
- The time zoom (timezoom.py:643) damps every lying snowpack by `summer_damp x sheet_cover`. `sheet_cover` is
  never below `icemass.LOCAL` = 0.3, even with no ice anywhere.
- The run's second test (`acc_ok`, h = 330 m on every cell) does use the floor, so LOCAL acts in the run only on
  cells next to ice.

Measured on the L4 seed-1 climate (300 Myr), averaged over the orbits: the land cells where bare-ground snow
outlasts the summer.

| Global shift | Run's rule (cells) | Time zoom's rule (cells) |
|---|---|---|
| dT 0 | 13 | 14 |
| -6 | 18 | 24 |
| -9 | 27 | 39 (+44%) |

So a time zoom from a run's moment glaciates bare ground more readily than the run's rule allows. That is one
cause of its documented drift to more ice (-68..-144 m in 150 kyr). LOCAL itself is the knob that "lets Earth's
time zoom glaciate" (overview §2.8; PW-240 option B), which makes it close to a bandaid.

Options:
- A. The run's seed uses the same `sheet_cover` (LOCAL floor). Consistent, but more run ice (worse for PW-240).
- B. The damping applies only on ice: bare ground gets cover 0 in the time zoom too, and LOCAL becomes a floor on
  ice only. Consistent, and the seasonal snow's albedo stays where the climate already has it. Earth's time zoom
  then glaciates less (PW-033 needs its own fix).
- C. Leave both as they are and document the difference.

Lean: B, together with PW-240's plan to lower LOCAL once Earth's inception has its own fix.

## Updates
- 2026-10-15: Status in-progress -> done. Done in the ice fix branch (merged 20684ed); docs/review/audit/fixes-ice.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-ice-veg-new-cap-rule-run-vs-timezoom.md (found by audit-ice-veg).
