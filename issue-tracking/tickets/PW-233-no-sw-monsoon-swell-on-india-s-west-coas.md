---
id: PW-233
title: "No SW-monsoon swell on India's west coast: the climate's July wind over the Arabian Sea is weak (0.29)"
type: task
status: todo
parent: PW-013
subsystem: climate
effort: m
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-075]
refs: [planet/climate.py, planet/coast.py, tools/coast_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Rest of PW-075. tools/coast_check.py: India W wave power 2.9 kW/m (obs 8-15). The wave model is fine there; its input is not: at (15.0, 73.3) the climate's July wind vector has length 0.29 (a steady trade is ~1) and almost no storminess, so the wave-driving wind is ~3.7 m/s in July. The real SW monsoon over the Arabian Sea is one of the strongest steady winds on Earth (the Findlater jet, 10-15 m/s near the surface in July), and its swell gives India's west coast most of its yearly wave energy. The model's summer monsoon_wind pulls air toward the warm continent, but the cross-equatorial flow over the western Arabian Sea doesn't come out strong. Check the July wind on Earth (earth_check prints no wind numbers yet; ERA5 July 10 m wind over 10-15 N, 60-70 E is ~10-12 m/s from the SW) and what limits it in climate.monsoon_wind (the 0.3 strength, the cap, the w ramp near the equator).
- [ ] July wind over the Arabian Sea SW and strong; coast_check India W within 2x

## Updates
- 2026-10-15: Created from inbox draft draft-india-monsoon-swell.md (found by smalls2).
