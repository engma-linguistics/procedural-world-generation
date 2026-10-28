---
id: PW-950
title: Shelves stay ~1.5% of the ocean because the submerged continent sits ~1.5 km deep; try water-loaded isostasy
type: task
status: todo
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: med
found_by: lane19b
blocked_by: []
relates: [PW-818, PW-846]
refs: [planet/surface.py, planet/tectonics/, tools/scorecard.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Lane 19 added clinoform progradation to surface._offshore (PW-818: sediment arriving at the shelf brink fills the
slope cell toward shelf level). Measured over seeds 1-6 at L6, 600-1000 Myr mean: shelf (0..-200 m) 1.40% -> 1.46% of the
ocean; median submerged continent -1500 -> -1464 m (Earth at L6: ~5.8% and -184 m). Scorecard seeds 1/2 at 1 Gyr:
shelf 0.7% and 2.0%. Sediment supply is not the limit: drowned continental crust sits ~1.5 km down, far below any
wedge the rivers can build. Likely cause: the submerged continent's isostasy is computed as if unloaded (or air-loaded),
so a flooded margin sinks too far; under water a column floats ~1/(rho_m - rho_w) not 1/(rho_m) higher per km of
crust thinned. Try water-loaded isostasy for sea cells of continental crust (no fudge to the shelf target).
- [ ] median submerged continental cell within -100..-500 m on ~70% of seeds at 1 Gyr
- [ ] shelf share of ocean >= 3% without a pass-rate cost on the paired judge

## Updates
- 2026-10-28: Lane 23, round 1 (failed): water-loaded isostasy. The premise has the sign backwards. Under water a column carries water, not air, so each km of thinning sinks it (rho_m-rho_c)/(rho_m-rho_w) = 220 m, not 150 m, and a drowned margin goes 1.45x deeper (the standard air- to water-loaded conversion, e.g. Allen & Allen, Basin Analysis). Tried anyway (docs/review/tectonics/crust/wl.py, L6 s1, branch code): submerged median -766/-875/-997 m (air) vs -1105/-1135/-1369 (water) at 200/300/400 Myr; shelf lower in 6 of 8 samples. Not kept. Separately, PW-970's weld fix moved the paired L6 set (36 draws, 600-1000 Myr): submerged median -1519 -> -819 m, shelf 1.58 -> 2.10% of ocean; at 1 Gyr the median is within -100..-500 m on 2/36 draws and shelf >= 3% on 10/36. Criteria still unmet. Why: drowned continent is mostly the stretch floor (22 km, -1.4 km) and 12-18 km margin rings. Earth's shelves are on beta ~1.2-2 crust held at sea level by 5-15 km sediment wedges (Steckler et al. 1999). Suggestions: (1) tapered stretching, thinning that falls off over a 50-200 km necking zone, so inner margin cells keep 27-33 km; (2) measure sediment delivered to the shelf brink against the ~2.3x-depth fill it needs; (3) wave-base planation at lowstands; (4) go water-loaded only after 1-2. Moved to v2 (owner rule: record and stop).
- 2026-10-28: Owner 10-28: if it fails a round or three, record what was tried, why it failed and suggestions, then move it to v2.
- 2026-10-28: Created from inbox draft draft-shelf-water-loaded-isostasy.md (found by lane19b).
