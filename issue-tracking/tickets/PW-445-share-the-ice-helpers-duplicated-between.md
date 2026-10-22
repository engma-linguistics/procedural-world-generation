---
id: PW-445
title: Share the ice helpers duplicated between the time zoom, icemass and tectonics/earth (after PW-438 merges)
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: timezoom
effort: m
impact: med
found_by: pw442
blocked_by: []
relates: [PW-442, PW-438, PW-440]
refs: [planet/icemass.py, planet/tectonics/earth.py, planet/timezoom/forcing.py, planet/timezoom/kernels.py, planet/timezoom/ice.py, planet/zoom.py, planet/climate.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-442 split `planet/timezoom.py` into a package without touching the run's climate and ice code (PW-438 was editing it). A duplicate scan found these copies; do them once PW-438 has merged, each only where the shared version gives bit-identical outputs (`uv run pytest -q`, no golden updates):

- [ ] **Ice albedo cooling**: `planet/timezoom/forcing.py albedo(p, f)` (tanh rule, `ice_albedo_max * tanh(ice_albedo * f / 0.03 / ice_albedo_max)`) is the same rule as `tectonics/earth.py:127 albedo(f)`. One function in `icemass.py` (the ice constants live there), both call it.
- [ ] **Positive degree days (Reeh 1991)**: `planet/timezoom/kernels.py climate_step` (one inline line, `DAYS * (sigma/sqrt(2pi) exp(-x^2/2) + 0.5 t erfc(-x/sqrt2))`, numba) and `tectonics/earth.py:462 degree_days` (12-month sum through `_erf`) are the same integral. One `pdd_year`/njit helper in `icemass.py`, both call it. Mind that the kernel is numba-compiled and the run's path is numpy: check last-bit agreement before sharing.
- [ ] **Nye edge profile**: `icemass.EDGE_H`'s derivation (rise = sqrt(2 tau/(rho g) d)), `tectonics/earth.py:372-390 sheet_surface rise()` (cell mean of the profile, 2/3 sqrt(k) ((d+1)^1.5 - d^1.5)) and `planet/zoom.py:977-1040` (snout mean, `GL_NYE_M = 2 tau/(rho g)`): one `nye_profile` / `nye_cell_mean` next to `SHEET_TAU` and `EDGE_H` in `icemass.py`.
- [ ] **Sea level from ice**: `planet/timezoom/ice.py above_flotation` (ice above flotation plus the sinking-bed term, Goelzer 2020) and `tectonics/earth.py:169 sea_ice = -0.9 * vol / ocean_area` are one idea with the time zoom adding flotation and the bed term. A shared `sea_level_from_ice(...)` in `icemass.py`, with the plain-volume rule as the no-flotation case. Near, not identical: decide whether the run should use the flotation version (it changes goldens, so that is a behaviour change, not a refactor).
- [ ] **Insolation**: `climate.py:1564-1582 insolation/_insolation` (daily-mean h0 identity, fixed declination, no eccentricity) is a near duplicate of `planet/orbit.py insolation` (Kepler, Berger). Could call `orbit.insolation` with e=0 at a fixed longitude; not identical (declination handling), needs a golden decision.
- [ ] **Constants**: `RHO_I`, `RHO_W` are defined in `planet/timezoom/params.py` and again in `tools/earth_data.py:141`; icemass/earth.py have their own ice density. One home (`icemass.py` or `geo.py`).

PW-442 also left `icemass.py` importing `climate_step` from `planet.timezoom.kernels`; when the PDD helper moves, consider putting `climate_step` itself in `icemass.py` (it is "icemass's rule", per its docstring), so the dependency runs time zoom -> icemass only.

## Updates
- 2026-10-20: Created from inbox draft draft-pw442-phase2-shared-ice-helpers.md (found by pw442).
