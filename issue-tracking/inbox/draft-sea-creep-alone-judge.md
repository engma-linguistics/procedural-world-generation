---
title: Judge sea-floor creep alone (slope_k) to see whether it, or necking, cools the world and drowns land
type: task
status: todo
parent: null
subsystem: surface
effort: m
impact: med
found_by: lane-100c
blocked_by: []
relates: [PW-950]
refs: [planet/surface.py, docs/review/tectonics/margin/report.md, docs/review/base-climate/v1-finish-16/paired.sh]
---

## Description
In plain words: the new sea-floor creep makes continental margins look much more like Earth's. But on the climate
judge the combined change (necking, rise and creep) also left the worlds about 2 C cooler and with 3 points less land,
and 3 fewer of 36 worlds passed. Three changes were judged together, so we can't tell which one does it. Judging the
creep alone answers that.

Lane 100c's paired L6 judge (18 draws x rolls 0.0005 and 0.001; `neck_km=200 rise=1 slope_k=1000` against main):
late dT -2.24 C [-3.61, -0.58], late CO2 index -0.24, land % -2.83 [-2.98, -2.52], arid -4.3 points, trees -1.7.
Soft pass 26/36 against 29/36. No hard failures in either arm. L6 screens (seeds 1 and 3, 600-1000 Myr) show the creep
alone lowers land too (34.6 -> 31.8 / 30.8% at slope_k=1000). Necking alone lowered it 0.4 points in round 2. So the
creep is the main land term. One likely cause, not yet checked: sediment moved from the shelf onto the deep floor
raises the sea level and starves the deltas that build coast out.

What to do: run the same 36-draw paired judge on `slope_k=1000` alone (and maybe 300) against main, using
docs/review/tectonics/margin/paired_margin.sh (paired.sh through margindiag.py) as in report.md round 3. Check the sea level (`sea_level`,
`sea_cont` in the steps) and the delta/shelf deposit for the land loss.
Lane 100d (docs/review/tectonics/margin/diagnosis-land.md): traced on seeds 1 and 3, plus 29 of 36 paired draws
of slope_k=300 alone (judge stopped on the owner's call, proposals only). Land -1.60 [-1.85, -1.16], late dT
-0.92 [-1.97, +0.66], late CO2 index -0.10 [-0.36, +0.16]. The land goes because more of the continental crust
drowns: the creep strips the margins' cover, and rises piled on the ocean floor are born as drowned continent inside
the area thermostat. It is not sea level: the sea is lower. The cooling goes through the arc CO2 source, which
follows the volume thermostat (draft-arc-co2-follows-volume-thermostat), not through the land.
- [ ] land and late dT shifts of creep alone, each with its paired 95% interval (29/36 at 300 done; finish it)
- [x] the land loss traced to its cause (drowned continental crust; see diagnosis-land.md)
- [ ] soft pass not below main's before defaults-on
