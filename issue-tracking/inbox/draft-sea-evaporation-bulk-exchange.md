---
title: "Rain kernel: the sea fills the air to src_q instantly each step; a bulk exchange over a fetch moves the overturning and the rain a lot"
type: task
status: todo
parent: null
blocked_by: []
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneA
relates: [PW-015, PW-458, PW-346]
refs: [planet/climate.py, tools/earth_check.py, tools/overturning_report.py, docs/review/base-climate/handoff-A.md]
---

## Description
For PW-015 (probably `--merge-into PW-015`), and found while working PW-458 (lane A, stage 1).

**The mechanism.**
- In `climate._rain`, the air over the sea takes up `open_sea × (src_q − q)` per step, with no time constant. Open
  sea refills the air to src_q every step, at once.
- Through sea ice (open share 0.1, leads) the uptake rate per second depends on the step. The physical-time kernel
  (1416523) steps at 4984 s at L6, against the old 17189 s, so the leads became ~3.4× faster.
- Sea evaporation is therefore set by what leaves the air, not by an exchange rate. It piles up where dry air first
  meets water, and it is small over open interior seas (Earth L6):

  | sea | evaporation (mm/yr) | precipitation (mm/yr) |
  |---|---|---|
  | Baffin Bay | 517 | 237 |
  | Labrador Sea | 92 | |
  | Nordic Seas | 268 | |

  Observed, the open subpolar seas evaporate several times more than these, and Baffin far less.
- That makes Baffin Bay salty (35.2 psu without the overturning), and its brine water the densest in the north. This
  is part of why Earth's overturning sinks in Baffin Bay (PW-458).

**Tried (uncommitted on lane A's branch).**
- A bulk exchange: per step, `1 − exp(−open × wind × dt / sea_fetch_km)` of the deficit is taken up.
  `sea_fetch_km` = 770 (a ~1 km boundary layer / C_E 1.3e-3) and `sea_wind_min` = 3 m/s.
- Earth L6, HEAD → bulk exchange:
  - **Overturning:** NH sinking 5.1 → 13.0 Sv. The Nordic Seas go 0.1 → 5.9 Sv, Baffin 2.6 → 2.4. The Norwegian Sea
    is 0% → 43% open in winter.
  - **Rain, better:**
    - log-rain correlation 0.617 → 0.659;
    - Köppen arid (group B) share 18.0 → 27.5%;
    - exact match 31 → 34%;
    - the Sahara and Arabia drop off the worst-regions list.
  - **Rain, worse:**
    - land mean 1138 → 1284 mm (GPCC 791), and its 90th percentile 2611 → 3795;
    - group match 71 → 70%;
    - cities in the wrong group 18 → 25;
    - runoff / rain 0.47 → 0.59;
    - the Sahel and East Africa wetter (×4 → ×5).
- **Generated L6 worlds:** two of three (28442c, 607540) lose their northern overturning (16 → 0 Sv). The shared
  deep-water reference makes the hemispheres compete (see handoff-A).

**Verdict.** It isn't merge-ready as it stands: the rain is mixed, and the overturning tips on generated worlds. The
mechanism is right, though: sea evaporation should be a bulk exchange, and the leads' uptake should be per unit of
time. What's open:
- with the exchange, the target humidity `rh` (0.85 of saturation at the sea surface) no longer stands for the
  equilibrium. Should it become the surface's ~0.98?
- whether the extra land rain comes from the global `mean_mm` renormalisation now that less vapour is taken up near
  the coasts.

- [ ] sea evaporation as a bulk exchange, with the rain no worse overall on earth_check and on a few L6 seeds
- [ ] re-check the overturning (`tools/overturning_report.py`) on Earth and on generated worlds
