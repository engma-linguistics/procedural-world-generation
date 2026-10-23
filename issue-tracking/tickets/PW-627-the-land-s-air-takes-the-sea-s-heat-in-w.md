---
id: PW-627
title: "The land's air takes the sea's heat in winter but lies stable over it in summer: rain r 0.630 -> 0.649 and the SH coasts' summers right, but W Europe's sea summers cool (-0.9 -> -2.1) and the time zoom's endings test goes red (33.2 / 19.7 m)"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: ocean
effort: s
impact: high
found_by: base-climate-laneA17
blocked_by: []
relates: [PW-595, PW-593, PW-594, PW-578, PW-592]
refs: [planet/climate.py, docs/review/base-climate/laneA17/step2_stable_summer.diff, docs/review/base-climate/laneA17/bars.md, docs/review/base-climate/stages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A17's step 2 (PW-595's land part, re-founded). Not on the branch; the code is
`docs/review/base-climate/laneA17/step2_stable_summer.diff` (relative to the branch head 7b41cea, step 1).

**Mechanism.** `_sea_half` gives the sea a share of the land's swing where the air came off land (`land_air`), the
same in both seasons (`open_b` against the mixed layer). But the exchange isn't symmetric:
- in winter the land's air is colder than the water: heated from below, it churns and takes the heat at `open_b`;
- in summer it is warmer and lies stable over the water (the model already says so for the vapour, PW-578): no
  turbulence carries its heat down, only its longwave, 4 sigma T^3 (~5 W/m2 per C, against open_b's 30).

So `_sea_half` returns a summer half (land part x lw / (lw + cap), c ~0.12) and a winter half (as before, c ~0.42).
The water's year is then colder by hk x (winter - summer) / 2 (`chill`), a surface cooling the currents carry like
upwelling's (each band's mean kept, as for upwelling). No new constant.

**Earth L6, step 1 -> step 2** (`laneA17/bars.md`):
- rain log-r 0.630 -> **0.649**; Köppen 33 / 71 -> 34 / 71; cities wrong 19 -> 16;
- SH coastal range 12.5 -> 12.1; sea's warmest month: off Patagonia +2.7 -> +0.1, Tasman +3.8 -> +2.6, Labrador Sea
  +2.8 -> +0.3; half-swing Patagonia 6.1 -> 4.8 (obs 3.7), Tasman 3.7 -> 3.1 (2.7), Agulhas 3.6 -> 3.1 (2.4);
- annual sea air: Tasman +3.1 -> +2.4, Agulhas +1.2 -> +0.5, Brazil +1.0 -> +0.3, Gulf Stream box +5.0 -> +4.5;
- Labrador warmest +4.3 -> +2.4, Iceland +3.4 -> +1.5;
- stage 1 holds: Earth NH 13.86 -> 13.64 Sv (89% open polar sea), Norwegian coast 100% open; the 9 worlds all sink
  in both hemispheres (dad91b's south 2.85 -> 1.89, the lowest).

**What regresses:**
- W Europe warmest -1.0 -> **-2.1**; Biscay-N Sea sea summer -2.5 -> **-5.4**; Fennoscandia warmest -3.8 -> -4.7;
- near-land NH sea swing within 1.5x 52 -> **33%**;
- SH land 150-400 / 400-800 km range bias +2.1 / +1.6 -> +2.7 / +2.6;
- Norwegian coast winter sea air 6.4 -> 7.6 (NCEP ~3.5): the band-mean compensation of the chill lands on the
  upwind seas;
- `test_glacials_grow_ice_and_endings_melt_it_fast`: glacial extra / left 33.2 / **19.7** m (bar left < extra / 2).
  Its world is a chaotic L5 run (lane A16: the world, not the climate, decides this test), so this needs A16's
  `xzoom.sh` crossing before it is blamed on the rule. Everything else passes (592).

The European regression is PW-595's own warning: those seas' summers were right only because the land part gave
them a continent's swing while their own (one 50 m layer, PW-593) is too small. With PW-593's wind-set layer on top
(`ml_wind`, `laneA17/bars_pw593_on_step2.md`) the NH comes back (W Europe +0.2, Biscay -0.9, near-N 69%), but the SH
breaks again (coastal range 14.5, Tasman sea summer +6.0) because the SH coasts' summer winds are still calm
(`draft-sh-coastal-summer-winds-still-calm.md`).

Options:
- A (lean): merge step 2 once the endings test is crossed and shown to be the world's chaos (rain r +0.019, the SH
  bars; W Europe and the North Sea worse until PW-593). The regression is the fixed 50 m summer layer's, a fitted
  constant, which is the owner's "global, not local optima" case.
- B: hold it and merge it together with PW-593's layer, as PW-595's checkbox asks, once the SH summer stirring is
  solved.
- [ ] A / B
- [ ] the endings test crossed (`laneA16/xzoom.sh`) on step 2's climate

## Updates
- 2026-10-23: Created from inbox draft draft-stable-summer-off-land-air.md (found by base-climate-laneA17).
