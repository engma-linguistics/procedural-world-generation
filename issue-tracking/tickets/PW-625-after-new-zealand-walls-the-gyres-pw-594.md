---
id: PW-625
title: "After New Zealand walls the gyres (PW-594 step 1) the Tasman is still +3.1 C (SST 18.5 vs NCEP air 15.2): the East Australian Current runs ~2 m/s to 38S and its warmth spreads east at 40-47S"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: ocean
effort: m
impact: med
found_by: base-climate-laneA17
blocked_by: []
relates: [PW-594, PW-595]
refs: [planet/climate.py, docs/review/base-climate/laneA17/wbc_step1.txt, docs/review/base-climate/laneA17/curmap.py, docs/review/base-climate/laneA17/gyre_base.txt]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A17 step 1 (commit 7b41cea): islands longer north to south than two boundary-current widths now wall the gyres
(New Zealand, Luzon, Sulawesi). Before, New Zealand's two islands were each under `island_km2`, so the whole South
Pacific gyre closed on Australia and Tasmania. Tasman 35-45S annual sea air +3.9 -> +3.1, SST 19.3 -> 18.5,
warmest month +4.7 -> +3.8. PW-594's bar (Tasman near-land SST within 2 C) is not met yet.

What is left (`wbc_step1.txt`, `curmap.py -50 -22.5 145 185`):
- The coastal cells along E Australia carry the current at 2.0-2.2 m/s poleward from 25S to 35S and 1.1-1.6 at
  35-40S; the gyre anomaly grows from +3.6 at 25S to +5.1 at 40S. Real cell-mean speeds (a ~100 km core of
  ~1-1.5 m/s) would be ~0.5-1. Above 1.5 m/s the heat's reach is capped at cur_max x relax_km = 7500 km, so the
  water barely cools on the way. `cur_max` 3 -> 1.5 alone would take the Tasman's SST another -1.2 C (sensitivity
  only, a number, not tried as a fix).
- The current turns east at 37-40S and the eastward flow at 40-50S runs 0.8-1 m/s (the ACC's real mean is
  ~0.1-0.3), so the warmth fills the Tasman out to 165E.
- On Earth the current leaves the coast at 31-34S (the Tasman Front towards New Zealand's north cape), a separation
  the linear Stommel solver doesn't make: it follows the coast to the zero-curl latitude (46S here, about right).
- Off Patagonia the Brazil Current runs south to 45S and there is no Falklands Current north of 47S (the ACC's
  branch through Drake, topographic). Tried: no Sverdrup gyre in latitudes where walls are under 3-5% of the circle
  (circumpolar flow instead): the Tasman unchanged and Patagonia +3 C warmer, so not that.
- The westerlies' equatorward Ekman drift (the ticket's other lead) is ~1.5 cm/s in a 50 m layer: too small to steer
  the carry, and its zonal mean is taken off with the band's.

Candidates: the gyre current's strength in the boundary layer (the WBC's speed at L6 against its transport), or a
separation rule (a WBC leaves the coast where it turns away from the meridian / the coast's direction changes).
- [ ] Tasman near-land SST within 2 C of NCEP's air

## Updates
- 2026-10-23: Created from inbox draft draft-pw594-tasman-still-warm.md (found by base-climate-laneA17).
