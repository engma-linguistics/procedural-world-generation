---
id: PW-153
title: Ocean layers (salinity, sinking, SST) and the overturning strength in run keyframes
type: task
status: todo
parent: null
subsystem: store
effort: m
impact: low
found_by: viewerocean
blocked_by: []
relates: [PW-137, PW-144]
refs: [planet/timeline.py, planet/tectonics/output.py, planet/tectonics/earth.py, planet/store.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-137/PW-144 store sea-surface salinity, sinking (Sv per cell), SST (annual, July,
January), dew point and humidity on worlds only (world.finish), plus the overturning
in world meta. Run keyframes don't have them: the simulation keeps only temp, winds,
currents etc. from each climate step (tectonics/earth.py sets sim.wind / sim.current;
output.climate_now copies them), not climate.compute's sss / overturning / moc_sites.

Cheapest useful step: the overturning strength (sum of sinking, north / south) as a
per-frame stat in run.json (a few bytes per frame), so the viewer and run.txt can plot
the overturning through time (shutdowns as continents move). Per-cell layers cost
~2 bytes x cells x frames each (L7, 250 frames: ~80 MB per <u2 layer), so salinity /
sinking keyframes are probably not worth it; SST maybe as i1 (whole C).
- [ ] sim keeps sss / overturning sum from the last climate step; frame stats get moc_sv, moc_north_sv, moc_south_sv
- [ ] viewer run summary shows it (and maybe a small chart)
- [ ] decide on per-cell keyframe layers (likely no)

## Updates
- 2026-10-14: Created from inbox draft draft-ocean-layers-in-keyframes.md (found by viewerocean).
