---
id: PW-1458
title: Measure L7's carbon-cycle yardstick on current code (it is derived, not measured)
type: task
status: done
parent: null
milestone: later
subsystem: climate
effort: s
impact: med
found_by: lane170
blocked_by: []
relates: [PW-1424]
refs: [docs/review/climate/stability/round3.md, tools/yardstick.py, "planet/tectonics/earth.py::YARDSTICK"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** Each grid level now has one fixed carbon-cycle yardstick (PW-1424 A). L6's was measured on the
judge's 36 runs with the new code. L7's could not be: no L7 judge set exists. It was derived from six older L7 runs
in the run store, made before the weathering read plant cover, plus the shift L6 showed when that change came in
(round3.md). Every 0.1 the constant is off moves every L7 planet's whole later climate about 1.1 C, in the same
direction. L7 is the showcase level.

**What breaks if never done.** Showcase and default L7 worlds could all sit about a degree warmer or colder than
the model means, and nobody would see it as a bias, because every L7 planet shifts together.

**Do.** Spin about 6 L7 stock draws to 300 Myr (fork.py spin, or the first 300 Myr of `paired.sh` with LEVEL=7
ONLY=l6fix), run `tools/yardstick.py` on them, and set YARDSTICK[7] to the mean if it is outside the standard error
of the current value. About 6 x 300 Myr at L7 (~1.5 runs' worth).

## Updates
- 2026-11-04: Status todo -> done. Merged (lane 187b, b4d1794b): YARDSTICK[7] 1.542 -> 1.618 (24 L7 spins, sd 0.178, SE 0.036); L6 stays 1.377. Paired 4-draw check vs old value: median late dT -0.59 C (expected ~-0.84), 0 hard failures both arms, soft 4/4 both. No 36-draw L7 judge (round4.md).
- 2026-11-04: Created from inbox draft draft-l7-yardstick-measure.md (found by lane170).
