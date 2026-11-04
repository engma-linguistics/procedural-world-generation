---
title: "Measure L7's carbon-cycle yardstick on current code (it is derived, not measured)"
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: s
impact: med
found_by: lane170
blocked_by: []
relates: [PW-1424]
refs: [docs/review/climate/stability/round3.md, tools/yardstick.py, "planet/tectonics/earth.py::YARDSTICK"]
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
