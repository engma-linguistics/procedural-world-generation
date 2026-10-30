---
id: PW-1034
title: "Physical constants are re-typed across modules: seconds per year has two values, 9.81 x16, ice density 917 x11, R_KM redefined, the 14.5 C baseline x5"
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: xs
impact: low
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-445, PW-481, PW-443]
refs: [planet/climate.py, planet/timezoom/kernels.py, planet/coast.py, planet/zoom/regional.py, planet/highlights.py, planet/ocean.py, planet/vegetation.py, planet/hydrology.py, planet/lineages/contacts.py, planet/timeline.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The same physical numbers (seconds in a year, gravity, density of ice, Earth's radius, the 14.5 °C reference temperature) are typed out separately in many files, and they don't all agree. When other planets arrive (PW-481) each of these has to become one knob, and today a change to one copy misses the others.

Verified on main b36c9581: seconds per year `3.156e7` (coast.py:578, zoom.py:177, highlights.py:148, ocean.py:557, vegetation.py:813, hydrology.py:110) vs `365.25*86400` (climate.py:2498) and `3.15576e7` (timezoom/kernels.py:337). Also reported by the auditors, not each re-checked: `9.81` 16x in 10 files; `917` 11x (icemass.RHO_I exists); `R_KM = 6371.0` again in lineages/contacts.py:35; `111.2`/`111.0` km per degree; `6.371e6` in hydrology; the 14.5 °C dT baseline bare in output.py:186, timeline.py:425/519, finish.py:140/272; `U_TRADE` = `U_REF` = 7 m/s; `4.1e6` sea heat capacity literals.

Fix: `planet/constants.py` (YEAR_S, GRAV, RHO_ICE, RHO_SEA, RHO_C_SEA, KM_PER_DEG from R_KM, T_REF_C, OMEGA) and use it. Folds the ice part of PW-445.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-physical-constants-module.md (found by code-audit-2026-10).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
