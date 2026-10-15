---
id: PW-051
title: Oceans get older after the l7jumps fix; sea-level basin term on its clip
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: l7jumps
blocked_by: []
relates: [PW-024, PW-053]
refs: [planet/tectonics/events.py, planet/tectonics/earth.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Margin subduction now breaks off one basin (6000 km of the oldest passive margin) instead of the plate's
whole ocean. Mean ocean age is 83 Myr at L6 (70 before; Earth ~60). In stagnant 2–3-plate phases the L7
mean reaches 140–185 Myr, and the ocean-basin term of sea level sits on its −250 m clip. (Only that
term — half the change in mean ocean depth against a ~300 Myr running baseline — is clipped to ±250 m;
the hot-mantle and ice terms are added after the clip.) More plates (PW-024) may fix most of it.

## Updates
- 2026-10-15: Tect2: mean ocean age now 41-57 Myr after PW-191's age fix; likely resolved, re-measure before closing.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Crust and continents.
