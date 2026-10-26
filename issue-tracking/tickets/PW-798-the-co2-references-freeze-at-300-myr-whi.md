---
id: PW-798
title: The CO2 references freeze at 300 Myr while a growing-continents planet's land is still emerging, locking in a ~1.3x weathering surplus (water world)
type: task
status: todo
parent: null
milestone: v3
subsystem: climate
effort: m
impact: med
found_by: v2-climate-1
blocked_by: []
relates: [PW-790, PW-558, PW-559, PW-576]
refs: [planet/tectonics/earth.py, docs/review/base-climate/v2-climate-1/]
created: 2026-10-24
updated: 2026-10-26
---

## Description
In `earth.global_temperature` the source and sink references follow the planet's rates over REF_MYR (100 Myr) and
are then frozen at REF_FREEZE (300 Myr). This assumes the made-up start has settled by then. With
`continental_start` (the water-world preset: 0.1, growth e-folding 700 Myr) the land is still growing at 300 Myr:
8% to 13% before the freeze, and about 30% by 1 Gyr. The reference lags the rising sink.

In v2-climate-1's look at v1-finish-8's water-world runs (`relsum.py`), sink/ref is already 1.29-1.48 during
100-300 Myr. After the freeze it stays at 1.2-1.3 (star off) and 1.5-2.7 (star on), against 0.96-1.06 for the
Earth-like runs. The planet carries a ~30% weathering surplus as permanent cooling, on top of the real draw-down
from new land. v2-climate-1 measured that heat_start 1 (no hot mantle) is just as cold, so this surplus, not the
mantle cooling, is what makes the recipe an icebox. The preset needs a climate_offset of +8 to live.

Options:
- A. Freeze the references once the start has settled, as measured from the planet: when the continental share
  is within some fraction of its target, or at REF_FREEZE + a multiple of continental_growth when
  continental_start is set. That is planet-relative, not a per-preset factor.
- B. Leave the references alone. The emerging-land cooling is real, so the recipe takes a climate_offset (+8, as
  measured at L6).
- C. Keep following the sink's land-area part only (supply per unit land fixed). PW-576 stage 3 tried and dropped
  a similar partial follower.

Lean: A. It is the root cause, and it should let the water world's offset return to about 0. Check that it is a
no-op for the Earth-like default (flat land, so it should be), and redo the L6 18-draw strict pass rate and an L7
check.
- [ ] references fixed at a settled start on a growing-continents planet
- [ ] water world at L6 and L7 over 2 Gyr not an always-icebox at offset 0; Earth-like pass rate not regressed

## Updates
- 2026-10-26: Milestone v2 -> v3: other planet kind. (PW-900 backlog reorg).
- 2026-10-24: Status needs-decision -> todo. Coordinator ruling: option A (freeze references once the planet's land has settled, planet-relative). Next physics ticket after the benchmark.
- 2026-10-24: Created from inbox draft draft-co2-ref-freeze-emerging-land.md (found by v2-climate-1).
