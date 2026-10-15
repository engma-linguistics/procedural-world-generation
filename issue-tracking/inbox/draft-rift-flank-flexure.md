---
title: Rift flanks need flexural unloading uplift (negative-load flexure)
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: tect2
blocked_by: []
relates: [PW-135, PW-054]
refs: [planet/tectonics/isostasy.py]
---

## Description
PW-054 added `isostasy.subsidence`: flexural moats beside thickened crust
(positive loads only) and a McKenzie thermal term that lifts the stretched
cells themselves (~0.8 km at beta 1.5) and lets them sag over 63 Myr. The
flanks of a rift still get nothing: on Earth a rift's thinned crust is a
negative load that the stiff plate spreads, lifting the shoulders 1-2 km
(Drakensberg, Western Ghats, Eastern Australia), which is what PW-135 needs
for great escarpments.

The same formula extends naturally: root R = ROOT x (thick - CONT_KM) for
recently rifted continent (negative), weighted by its age (exp(-age / ~200
Myr), so old, relaxed margins don't keep a permanent bulge), and apply the
positive part of flexure x (R - smooth(R)) on the cells that aren't
themselves thinned. Careful: rifted-margin crust (12-18 km) is a huge
negative load; restrict to stretched crust with a rift record, and check the
coastal land share and the escarpment class (landform) at L6 and L7.
- [ ] escarpment class share and heights re-measured (PW-135)
