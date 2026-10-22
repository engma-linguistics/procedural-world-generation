---
title: "Stage 2b landed attempt 2 with the rain regression accepted; the rain reacts through the sea's evaporation source (qs / src_q), and the water's swing near land is too big"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneA3
blocked_by: []
relates: [PW-578, PW-346, PW-015, PW-575, PW-577]
refs: [planet/climate.py, docs/review/base-climate/stages.md, docs/review/base-climate/stage2b/, tools/earth_check.py]
---

## Description
For PW-578 (`--merge-into PW-578`).

**Landed (lane A, stage 2b, owner's order).** Attempt 2 (`stage2/attempt2.patch`) is re-applied on main 2684f2b
unchanged. The rain and Köppen regression is accepted for now (Earth L6, earth_check main → after):
- log-rain correlation 0.617 → 0.533;
- Köppen group / exact 71 / 31% → 66 / 28%; the arid (B) share 18.0 → 15.6% (Kottek 30.1);
- cities exact / group / wrong 32 / 29 / 17 → 25 / 34 / 19;
- the summer share of land rain 0.75 → 0.80 (GPCC 0.65).

Three tests fail with it, all downstream of the rain:
- `test_envelopes.py::test_earth_climate_score`: Köppen group 65.7 against its floor of 66;
- `test_rain_transport.py::test_same_planet_rains_the_same_at_two_levels`: inland rain L5 / L6 differs 5.02% against
  5% (main 3.0%). Both levels' inland rain falls ~10% with the temperatures unchanged;
- `test_zoom_soils.py::test_zoom_soil_layers`: the big rivers' floodplains are 48% alluvium / gley / peat against
  > 50%.

**Which part of the rain kernel reacts (option B's first half).** Bisected on Earth L6 by giving one input at a time
main's uniform 6 C × s half-year SSTs (`_season_inputs`):

| the old swing in | log-rain r | Köppen group | summer share |
|---|---|---|---|
| nothing (attempt 2) | 0.533 | 66.4 | 0.80 |
| `qs` / `src_q` and `t_sl` over the sea (the vapour the sea gives the air) | **0.598** | 68.0 | 0.77 |
| `mse_t` over the sea (the showers' instability) | 0.531 | 66.2 | 0.80 |
| the zonal SST behind `mse_thr` (the air aloft) | 0.529 | 66.6 | 0.79 |
| all three | 0.593 | 68.4 | 0.76 |

So it is the sea's evaporation source, not the convection threshold. (The rest, to 0.616, is the winds' land-sea
contrast, which also reads the sea's swing.)

**Why: the water takes the land air's whole swing.** Sea cells 20–65 deg, binned by `land_air`, the half-year SST
range against NCEP's sea-air range (which the water's range is at most):

| band, land_air | main SST range | attempt 2 | NCEP air range |
|---|---|---|---|
| 20–35, < 0.05 (open ocean) | 5.4 | **1.8** | 5.7 |
| 20–35, > 0.5 (next to land) | 5.3 | **16.3** | 9.7 |
| 35–50, < 0.05 | 7.9 | **2.6** | 6.0 |
| 35–50, > 0.5 | 7.7 | **21.9** | 17.4 |
| 50–65, < 0.05 | 9.2 | 3.2 | 5.3 |
| 50–65, > 0.5 | 6.3 | 9.6 | 19.8 |

- The seas beside land get summers 2–3 C too warm (20–50 deg, `land_air` > 0.3), which feed the summer monsoons on
  the land next to them: the summer share 0.75 → 0.80, the SH subtropics +40–50%.
- The open subtropical and mid-latitude oceans swing far too little (1.9 C × s was set from the Southern Ocean).

So this is a wrong mechanism, not only a fit:
1. `sea_half + continental × land_air` is the swing of the **air** over the sea. The water swings less: its mixed
   layer only takes part of the air's swing (the air-sea exchange, ~`open_b` 30 W/m2/C, against the mixed layer's
   seasonal heat capacity, ρ c h ω ≈ 40 W/m2/C for 50 m), and its winter side is already carried separately
   (`_winter_air`).
2. The water's own swing depends on its mixed layer's depth (shallow in the summer-stratified subtropics, deep in the
   stormy Southern Ocean), not on one number.

A first probe of that split, in the rain's inputs only (water half-swing `s × (own + c × continental × land_air)`):

| own, c | log-rain r | Köppen group | summer share |
|---|---|---|---|
| 1.9, 1 (attempt 2) | 0.533 | 66.4 | 0.80 |
| 1.9, 0.43 (the exchange against the mixed layer) | 0.576 | 67.2 | 0.78 |
| 4, 0.43 | 0.570 | 67.2 | 0.78 |
| 5, 0.3 | 0.576 | 67.2 | 0.78 |
| 6, 0 (main's uniform swing) | 0.594 | 68.2 | 0.76 |

So the split recovers about half. Any coupling of the water's swing to the land's air still costs rain, so part of
the kernel is also fitted to the uniform swing; finding that part is the rest of option B.

What to try (the fix stage of PW-578): split the water's half-swing from the sea air's, from those two planet-general
quantities, and feed the water's to `sst_jul` / `sst_jan`, the rain and the winds.
- [ ] earth_check log-rain r ≥ 0.617 and Köppen group ≥ 71% with the stage-2 bar still met
- [ ] the three tests above pass without loosening
