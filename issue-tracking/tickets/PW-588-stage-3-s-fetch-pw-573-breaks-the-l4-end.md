---
id: PW-588
title: Stage 3's fetch (PW-573) breaks the L4 endings test by moving the glacial's extra ice to polar cells, not through the ice-surface rules
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneA11
blocked_by: []
relates: [PW-573, PW-352, PW-581, PW-580, PW-569, PW-439, PW-568]
refs: [planet/climate.py, tests/test_timezoom_cycle.py, docs/review/base-climate/stages.md, docs/review/base-climate/laneA11/]
created: 2026-10-22
updated: 2026-10-22
---

## Description
Stage 3 attempt 2 (`laneA10/stage3_attempt2.diff`) fails `test_glacials_grow_ice_and_endings_melt_it_fast`:
58.9 m extra, 63.6 m left after 15 kyr. Lane A11 toggled its mechanisms (`laneA11/stage3_attempt2_toggles.diff`,
env S3_REACH / S3_FETCH / S3_SPLIT / S3_MTN). The values are extra / left, and the bar is left < extra / 2.

| variant | extra / left |
|---|---|
| main | 97 / 25, and 83 / 24 on a ULP-level rerun |
| attempt 2 | 59 / 64 |
| no per-time reach | 40 / 14 |
| no fetch | 27 / 2.6, rerun 51 / 4.6 |
| no split | 37 / 12 |
| no mountain rule | 75 / 21 |

Removing any one mechanism passes, but attempt 2 itself is no knife edge:
- With the source's −4 C shifted by ±0.1–0.2 C, it fails every time (66/68, 65/68, 41/36).
- Main and "no fetch" pass every time.

Not the ice-surface rules:
- `sheet_air=cold` → 78 / 69.
- `surface_air=fetch` → 88 / 86.
- `summer_damp=0` → 110 / 103.
- Main passes under all three.

What does happen: the glacial's extra ice goes poleward.
- At the ending, main's NH extra sits at 45–65N, which melts. Attempt 2's sits at 65–90N and 55–90S.
- After the ending, 115 of 135 km-sum of attempt 2's leftover lies poleward of 60 (main: 58 of 61).
- Most of that leftover lies where the no-index run's own mass balance is negative. So it is held by the sheet's own
  height and albedo (hysteresis), not by slow accumulation.
- At L4 (cells ~450 km) nearly all land is "coast" for a 1-day fetch. The fetch takes most of the continental swing
  off the polar lands, so their summers sit near the sea's. Those cells glaciate in a glacial and keep their ice at I=0.

A physics flaw in attempt 2's fetch: `land_sum = t_land + half_l * fetch`.
- At low fetch this falls toward the land's annual mean, below the summer sea air the wind brings, so summer land
  cools the sea air.
- That is wrong for snow-free land and is most of W Europe's −3.3.
- The sounder form builds the land's swing from the arriving sea air: `sea_in + fetch * (land_full - sea_in)`.
  It is measured in `laneA11/stage3_probe_fetch_from_sea_air.txt`:
  - W Europe −3.3 → −2.2, Fennoscandia −6.7 → −5.1, rain r 0.621.
  - But SH coastal range 13.0 (1.35×), and the endings test is worse (90 / 82).

What to try:
- Give the fetch a resolution-independent meaning: the land's own swing builds over the continental scale PW-573
  names (1000–2000 km), measured on the land's width, not on one 1-day boundary-layer time. Then check that a coarse
  L4 grid doesn't make every land a coast.
- Re-run the toggles (`laneA11/tools/endiag.py`, `rd.sh`, `eq.py`).
- [ ] the fetch, in a form that keeps snow-free summer land at or above the arriving sea air, passes the L4 endings test

## Updates
- 2026-10-22: Created from inbox draft draft-stage3-fetch-moves-l4-glacial-ice-poleward.md (found by base-climate-laneA11).
