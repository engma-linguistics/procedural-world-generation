---
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
refs: [planet/tectonics/earth.py, tools/sealevel.py]
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
