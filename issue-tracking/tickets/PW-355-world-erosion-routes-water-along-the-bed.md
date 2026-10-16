---
id: PW-355
title: World erosion routes water along the bed under ice, the world's rivers over the ice surface
type: task
status: needs-decision
parent: null
subsystem: hydrology
effort: s
impact: low
found_by: pw307-world-land
blocked_by: []
relates: [PW-307]
refs: [planet/hydrology.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`hydrology.erode` (the world's display pass for sub-cell valleys) routes the water over the bed,
also under the ice, while `hydrology.rivers_and_lakes` (the world's rivers and lakes) routes it over
the ice surface. Since PW-307 a bed below sea level under grounded ice is land, and the routing
takes heights <= 0 for the sea, so `erode` routes over the ice surface only there (PW-307 kept the
change that small so worlds move only around marine ice). The mix is arbitrary at the boundary:
on time zoom 080df3 @ 950 kyr (L7) the changed routing past the marine bed drained a few
proglacial lakes 4-8 cells away (lake cells 177 -> 146) and moved the bed under the ice by up to
~140 m.
Options:
A. Route `erode` over the ice surface under all ice, as the rivers are (consistent; changes every
   iced world's beds under and just beyond its ice, and the rivers it cuts toward the margins).
B. Route over the bed under all ice, with a sub-sea bed under ice raised to just above the sea
   only for the routing (subglacial water follows the bed; needs a floor in the routing height).
C. Route by the subglacial hydraulic head, bed + 0.917 x ice (physically the water's potential
   under a sheet; positive wherever the ice is grounded with some margin).
D. Keep PW-307's mix.
Lean: A (one rule for the world's water, simplest), measured on an icehouse world.

## Updates
- 2026-10-16: Created from inbox draft draft-erode-routing-under-ice.md (found by pw307-world-land).
