---
title: Closed-basin share doubles from L6 to L7 (grid resolution, not tectonics)
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: med
found_by: tect2
blocked_by: []
relates: [PW-054]
refs: [planet/hydrology.py, planet/tectonics/isostasy.py]
---

## Description
Measured with the sim's own climate and `hydrology.rivers_and_lakes` on
`sim.bed()` every 20 Myr (tect2, after PW-054's subsidence, flexure 0.15):
- L6 seeds 1/2/21/3199, 100-1000 Myr: 9.5-11% of land drains inland,
  17-21% of arid (< 400 mm) land (5.5-6.4% / 9-12% before PW-054);
- L7 seed 3199, 100-340 Myr: 35% of land, 46% of arid land (23% / 35%
  before; at flexure 0.3: 48% / 65%).
Earth ~18% of land, about half of its arid land. The same tectonics gives
twice the inland drainage at L7, before and after the change, so the gap is
in how the cell-mean terrain resolves hollows (MIN_DEPTH, MIN_SLOPE x radius,
outlet cutting all act per cell). The flexure share was set so L7 (the
showcase level) isn't far above Earth, which leaves L6 short. Worth a look at
whether the hollow rules can be made level-consistent (e.g. MIN_DEPTH or the
outlet channel scaled with cell size), then retune `flexure` once.
