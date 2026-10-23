---
id: PW-586
title: climate.humidity reports RH a hair under HUMID_MIN at the floor (the soft saturation is applied after the floor)
type: task
status: done
parent: PW-470
milestone: v1
subsystem: climate
effort: xs
impact: low
found_by: base-climate-laneA11
blocked_by: []
relates: [PW-352]
refs: [planet/climate.py, tests/test_ocean.py]
created: 2026-10-22
updated: 2026-10-22
---

## Description
`humidity()` clips x = q / qs at HUMID_MIN (0.15) and then applies the soft saturation x / (1 + x^4)^(1/4). At the
floor that gives 14.998%, which is under `test_seasonal_sst_and_humidity`'s `rh >= 100 * HUMID_MIN - 1e-6`.

Main has no cell at the floor, so the test passes. Stage 3 attempt 3's energy split warms a dry cell enough to hit
it (basins fixture). The fix, measured on lane A11's candidate: `rh = max(x / (1 + x^4)^(1/4), HUMID_MIN)`, the floor
after the soft saturation. It's in `laneA11/stage3_attempt3_candidate.diff`. It matters only together with stage 3,
so fold it into stage 3's merge.
- [ ] floor applied after the soft saturation

## Updates
- 2026-10-22: Status todo -> done. 2026-10-22 stage 3 merged (lane A12): summer fetch from the arriving sea air on distance scales (fetch_km 1000, fetch_h 3500), per-time reach, PET-referenced energy split, mountain rule, humidity floor. Humid summers +5-6 -> +2-4 C; SH coastal range 1.29x (pass); dry-region summer rain down; r 0.620. W Europe / Fennoscandia summers worse via too-cold near-land NH SST (new ticket). Merged under the owner's principle.
- 2026-10-22: Created from inbox draft draft-humidity-floor-under-humid-min.md (found by base-climate-laneA11).
