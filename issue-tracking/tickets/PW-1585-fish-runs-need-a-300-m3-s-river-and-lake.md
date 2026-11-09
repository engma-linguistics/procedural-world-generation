---
id: PW-1585
title: "Fish runs need a 300 m3/s river and lake fisheries a 3,150 km2 lake: lower them towards real-world sizes, or keep the grid floor?"
type: task
status: todo
parent: PW-692
milestone: later
subsystem: food
effort: s
impact: med
found_by: scout-242
blocked_by: []
relates: [PW-820]
refs: ["planet/lineages/seafood.py::seafood", "planet/lineages/seafood.py::RUN_Q", "planet/lineages/seafood.py::LAKE_KM2", docs/review/pw820-water-units/README.md, tools/water_units_check.py, "FAO CIFA lake yield models https://www.fao.org/4/u6650e/U6650E07.htm", "Swift 1977 USGS OFR 77-422"]
created: 2026-11-09
updated: 2026-11-09
---

## In plain words
PW-820 put the fish-run and lake-fishery rules in real units at the values they already had at L7: a river needs about
300 m3/s at its mouth for a run that feeds a people, and a lake needs 3,150 km2 to be even a poor fishery. Real salmon
spawn in ordinary streams far smaller than that, and real lakes of 100 km2 land hundreds of tonnes of fish a year. So
the model under-gives fish to peoples on small rivers and lakes. Lowering the numbers would loosen them, so it is your call.

## Description
- Rivers: one L6 cell on its own sheds ~100 m3/s, so a threshold under ~200 m3/s can't be asked alike at L6 and L7 (L7
  draws rivers L6 can't). Swift 1977 (USGS OFR 77-422): five salmon species spawn across 84 reaches of 28 ordinary
  Washington streams; no minimum discharge is given.
- Lakes: FAO CIFA (African lakes and reservoirs, 71 waters): catch = 8.32 x area^0.92 t/yr (km2), a 100 km2 lake
  ~585 t/yr, a 1,000 km2 lake ~4,900 t/yr. Lakes on the grid start at one cell (3,113 km2 at L7, 12,452 at L6), so any
  drawn fresh lake already gets the 0.35 base; only the poor-to-full ramp (3,150 to 18,700 km2) would move.

Options:
- A (lean): keep the L7 values. Level-consistent (tools/water_units_check.py passes), conservative on fish.
- B: lower the run threshold to the finest drawn level's floor (e.g. 100 m3/s) and the lake ramp to 300-3,000 km2.
  More fish for small-river peoples at L7/L8; L6 then disagrees with L7 more (it can't draw those rivers or lakes).
- C: a sub-cell estimate: give each river cell a share of small tributary runs from its catchment (no threshold), so
  small rivers count at every level. More work (m), the honest version of B.

If never done: peoples on small rivers and lakes read as less fish-reliant than their real analogues; no crash.

Coordinator 11-09: A (keep the L7 values, now in real units; the owner defers physics calls). Revisit if refined L8/L9 worlds show too few fish runs.

## Updates
- 2026-11-09: Created from inbox draft draft-real-world-fish-run-and-lake-thresholds.md (found by scout-242).
