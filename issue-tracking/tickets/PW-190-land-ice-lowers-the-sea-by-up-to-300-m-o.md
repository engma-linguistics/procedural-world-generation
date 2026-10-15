---
id: PW-190
title: Land ice lowers the sea by up to 300+ m on some seeds (about 4x Antarctica's volume)
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: med
found_by: tectsea
blocked_by: []
relates: [PW-053]
refs: [planet/tectonics/earth.py, tools/sealevel.py, planet/timezoom.py, "world 8e71fd", "run ee65aa", "world bcc894"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
After the ocean-basin part of sea level was smoothed and soft-limited (PW-053,
tectsea), the largest remaining fast sea-level swings on some seeds come from
land ice (`sim.sea_ice = -0.9 x ice volume / ocean area`, earth.update_climate).
`tools/sealevel.py`, L6, 1 Gyr, default params:
- seed 11: sea_ice 0 -> -168 m (140 -> 160 Myr) -> -338 m (220 Myr), back to 0 by
  320 Myr; the largest 20-Myr sea-level change of the run (-280 m at 140-160) is
  158 m ice + 122 m basins;
- seed 2: sea_ice down to -191 m (before the change: -274 m); seed 21 -149 m.
- with the PW-024 plate nudge as well (final tectsea code): seed 2 sea_ice -218 m within
  20 Myr at ~736 Myr (the run's largest 20-Myr sea-level change, -264 m), seed 11 -190 m
  within 20 Myr at ~160 Myr; the ocean-basin part now moves at most 98-140 m in 20 Myr.
-338 m is ~120 M km3 of ice, ~4x Antarctica's, ~1.7x Earth's total at the Last
Glacial Maximum (~-130 m below today, plus ~65 m still in ice). The model's sheets
are meant as the average over ~100 kyr ice-age cycles, which should sit between
interglacial and glacial volume, not well beyond the glacial peak.
Check: sheet thickness (Nye profile with ICE_TAU = 50 kPa, up to 4 km) over a
polar supercontinent; whether the area is plausible (ice_pct then); and whether
ice building to ~-300 m within 40 Myr is the ice following continental drift
(fine) or a runaway in the albedo feedback (ICE_FEEDBACK, ice_albedo).
- [ ] the largest sea_ice on 4 L6 seeds x 1 Gyr understood, and either justified or
  brought to roughly the LGM's scale (~-150..-200 m)

## Updates
- 2026-10-14: Coordinator decision (north star): option C. The run's ice rule gets an ablation zone / becomes flow-consistent here, which fixes both the too-large run ice and the time zoom's cold-era spread (8e71fd: -258 m). Until then A: cold-era finished worlds glaciate hard, as documented in overview 2.14. B (spin-up balance) skipped as a half measure.
- 2026-10-14: Merged inbox draft draft-timezoom-cold-era-spread.md ("Time zoom: cold-era generated worlds still drop ~250 m, because the run's ice has no ablation zone", found by finish).
  After the PW-031 nudge (sea level from the water the ice holds; a run's start counted as the
  cycle average, so half the CO2 / ice-albedo caps), the time zoom of world bcc894 (run e0e21e
  @ 688 Myr, dT -3.3) peaks at -132 m (was -171) and an Earth-like moment (e0e21e @ 592, dT -0.7)
  at -95 m. But world 8e71fd (run ee65aa @ 632 Myr, dT -5.8, LGM-cold, sea already -274 m) still
  reaches -258 m (was -272), and almost all of it is not the feedbacks: with CO2 and ice albedo
  off, and even with the orbit off, it still falls -210 m in 60-80 kyr.
  
  Diagnosis: the main run's ice (PW-102 rule: where summers stay below 1 C and snow beats melt,
  no flow) is all accumulation zone. Every starting ice cell gains (median +0.17 m/yr; the
  start_anchor is zero there), ~10,800 Gt/yr of snow against ~1,700 Gt/yr of melt. The flowing
  sheets must spread until melt and calving balance them: 6.3% -> ~14% of the surface (all land
  poleward of ~55 deg, which the run had partly bare with summers of 2-4 C). Starting warmer over
  the ice (+3 or +6 C over the start sheets) only slows it.
  
  Options:
  - A. Accept: a cold-era moment's ice-age maximum really is far bigger than the run's average
    ice; document it (done in overview 2.14) and let finished worlds show it.
  - B. Balance the start: a sheet-by-sheet temperature correction (two-sided anchor) found by a
    short spin-up, so the start ice neither grows nor shrinks at the mean orbit; cycles then swing
    around the run's ice. ~1 min extra at L7; changes the meaning of the anchor for Earth too.
  - C. Fix the source: make the main run's ice rule flow-consistent (extend it by an ablation
    zone; ties to PW-190's too-thick run ice and PW-189 isostasy). Biggest, but fixes both.
  Lean: C as the real fix (with PW-190), A meanwhile; B only if finished cold-era worlds must look
  moderate soon.
- 2026-10-14: Created from inbox draft draft-ice-sea-level-depth.md (found by tectsea).
