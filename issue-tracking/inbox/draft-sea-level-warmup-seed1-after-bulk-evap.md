---
title: "test_sea_level's warm-up per-seed bar fails after the sea's bulk exchange: L4 seed 1's basin mean is -55 m (bar -50; main +7)"
type: task
status: done
parent: null
milestone: v1
subsystem: tectonics
effort: s
impact: med
found_by: lane25
blocked_by: []
relates: [PW-015, PW-549, PW-980]
refs: [tests/test_sea_level.py, planet/climate.py, docs/review/base-climate/deserts/README.md]
---

## Description
`tests/test_sea_level.py::test_sea_level_starts_at_zero_and_reads_high_in_the_warm_up` asserts each of seeds 1-3
(L4, 300 Myr) has a basin-term mean in -50..200 m. After lane 25's sea-evaporation bulk exchange (commit 5840dcc6,
PW-015) seed 1 reads -55 m. The set mean (+1 m) still passes its 0..150 bar.

Measured (L4, seeds 1/2/3, basin-term mean over the first 300 Myr, m):
- main: +7 / +38 / +15; climate_offset re-rolls 0.0005, 0.001, 0.0015: seed 1 +11, +15, +26.
- branch: -55 / +23 / +35; the same re-rolls: seed 1 -53, -58, -52.

So it isn't a single chaotic flip: on this branch, seed 1's warm-up takes a different path (at 102 Myr, land 21% vs 27%
and the continents hold more sea, sea_cont -211 vs -142 m). The rain change reaches the sea level through erosion and
the land. At L4 one seed's history is a fragile fixture.

Options:
- A. Keep the bar; find out why seed 1's L4 warm-up floods (erosion supply against the drier deserts?) before merging.
- B. Judge the warm-up on more seeds, keeping the -50 m bar per seed at ~70% (the acceptance rule), as the
  test-harness rule allows (assertions unchanged, a wider sample). The owner rules on thresholds.
- C. Merge, and treat it as the warm-up's known chaos on L4.

Lean: B (a 3-seed per-seed bar at L4 is a fixture, not a measure); then A if the wider sample also drops.

## Updates
- 2026-10-29: owner ruling, option B. The per-seed band is judged over seeds 1-10 at >=70%, assertions unchanged; marked slow
  (about 5 min). L4 basin means, seeds 1-10: main 7, 38, 15, 31, 37, -23, 36, -31, -33, 55 (10/10, set mean +13); branch -55,
  23, 35, 44, -17, -24, -8, -34, 52, 11 (9/10, set mean +3). The set mean sits lower, still inside its 0..150 bar.
