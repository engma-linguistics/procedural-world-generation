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
updated: 2026-10-31
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
- 2026-10-31: Lane 100 round (branch worktree-agent-a5fd6321b3834f864 @ daaf016f, held until after the v1 tag): necking (crust.necking, neck_km) + continental rise, both off by default. L6 s1-3: next-cell cliff 23 -> 15% (Earth 3.5), 200-3000 m band 12.3 -> 14.7% (Earth 19.6), shelf 2.6 -> 3.1%. Criteria unmet; residual wall is the brink fill's one-cell front (draft: foreset slope). Paired judge 11 draws: CO2 dips 0 -> 3 under 100 ppm (85/69/82, all recover; p 0.25), to recheck under D32 B. docs/review/tectonics/margin/report.md
- 2026-10-31: Lane 96 (L8 world a16f5a vs L7 2a7385 vs Earth ETOPO1 resampled to each grid, read-only; docs/review/l8-world/explore.md): the L8 world's shelf share is 4.3% of the ocean (Earth on L8 7.0%; 2a7385 0.66%) and its submerged continent median -154 m, but that is the run's +312 m highstand flooding low continent (shelf 2.1% at t=0), not margin physics. The margin itself is a one-cell cliff: medians across the continent-ocean crust boundary go 33.3 km / +30 m, 31.5 / +3, 25.9 km / -441 m (last continental cell) -> 9.0 km / -4199 m (first oceanic cell), edge rift strain median 0.04 (beta ~1.04: barely stretched). 20.9% of coast cells have water deeper than 3000 m within one 30 km cell and 41% within two (Earth on L8: 1.1% and 5.0%); median coast-to-3000 m 90 km (Earth on L8 360 km). Depths 200-3000 m are 5.0% of the ocean (Earth on L8 17.7%), 4000-5000 m 48% (Earth 32%). Steepest-neighbour gradient on slope cells (-500..-2500 m within 180 km of land) p50 60 m/km (Earth on L8 29). L7 2a7385 (older code, 792 Myr) has a wider taper (35 -> 19 km over 4 cells) but the same missing 200-3000 m band (10.6% vs Earth on L7 18.1%). Supports suggestion 1 (tapered stretching over a 50-200 km necking zone) plus a sediment apron at the slope foot (continental rise); L8 shows the step most plainly because the cell is narrower than the transition should be.
- 2026-10-29: McKenzie 1978 on file (read 10-29). Table 1 (p. 27) and eq. 12 (p. 28): E0 = 4 a rho0 alpha T1 / (pi^2 (rho0 - rho_w)) = 3.2 km, water-loaded; isostasy's SAG_KM 2.2 is the same with rho0 in the denominator (3.2 x 2.33/3.33 = 2.24), and SAG_TIME 63 is tau = 62.8 My. So the paper agrees with lane 23: water loading deepens a drowned margin's sag (1.43x), it doesn't lift it. McKenzie also has an initial subsidence Si, positive where the crust is thicker than 18 km (p. 27), and sediment-filled basins sink further (Fig. 4, p. 29).
- 2026-10-28: Lane 23, round 1 (failed): water-loaded isostasy. The premise has the sign backwards. Under water a column carries water, not air, so each km of thinning sinks it (rho_m-rho_c)/(rho_m-rho_w) = 220 m, not 150 m, and a drowned margin goes 1.45x deeper (the standard air- to water-loaded conversion, e.g. Allen & Allen, Basin Analysis). Tried anyway (docs/review/tectonics/crust/wl.py, L6 s1, branch code): submerged median -766/-875/-997 m (air) vs -1105/-1135/-1369 (water) at 200/300/400 Myr; shelf lower in 6 of 8 samples. Not kept. Separately, PW-970's weld fix moved the paired L6 set (36 draws, 600-1000 Myr): submerged median -1519 -> -819 m, shelf 1.58 -> 2.10% of ocean; at 1 Gyr the median is within -100..-500 m on 2/36 draws and shelf >= 3% on 10/36. Criteria still unmet. Why: drowned continent is mostly the stretch floor (22 km, -1.4 km) and 12-18 km margin rings. Earth's shelves are on beta ~1.2-2 crust held at sea level by 5-15 km sediment wedges (Steckler et al. 1999). Suggestions: (1) tapered stretching, thinning that falls off over a 50-200 km necking zone, so inner margin cells keep 27-33 km; (2) measure sediment delivered to the shelf brink against the ~2.3x-depth fill it needs; (3) wave-base planation at lowstands; (4) go water-loaded only after 1-2. Moved to v2 (owner rule: record and stop).
- 2026-10-28: Owner 10-28: if it fails a round or three, record what was tried, why it failed and suggestions, then move it to v2.
- 2026-10-28: Created from inbox draft draft-shelf-water-loaded-isostasy.md (found by lane19b).
