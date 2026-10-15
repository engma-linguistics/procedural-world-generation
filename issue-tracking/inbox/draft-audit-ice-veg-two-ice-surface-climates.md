---
title: "Ice surface: two climates for the same ice (climate.ice_surface's 10 C vs icemass's 2 C + damping)"
type: task
status: todo
parent: PW-245
subsystem: climate
effort: s
impact: low
found_by: audit-ice-veg
blocked_by: []
relates: [PW-112, PW-226]
refs: [planet/climate.py, planet/icemass.py, planet/tectonics/earth.py, docs/review/audit/ice-veg.md]
---

## Description
Since PW-190 the run's ice extent comes from `icemass` (2 C all-year cooling on thick ice, plus a summer damping by
sheet_cover and the melt hold). But the run's keyframe temperatures on ice, its Koppen, the zoom's ice surfaces and
the softness factor inside `ice_sheets` (earth.py:286) still use `climate.ice_surface`. That rule (climate.py:2046)
is 10 C x ice_cover colder all year, with the summer capped at half of its positive part.

The time zoom's frames, and the finished worlds made from them, report icemass-style temperatures instead. On a
big sheet in winter the two rules differ by up to ~8 C (part of PW-226's -105 C). PW-112 already says the 10 C
compensates a warm polar base. It no longer sets the ice extent; it only sets what is shown.

Fix: report the ice surface's temperatures from `timezoom_kernels.climate_step`'s own outputs (t_ann, t_warm,
t_cold at the ice's thickness, as icemass.balance already returns), and drop ice_surface's 10 C for land ice (the
zoom's `ice_ground` inverse with it). Effect: warmer winters shown on ice-sheet interiors, Koppen still EF.
