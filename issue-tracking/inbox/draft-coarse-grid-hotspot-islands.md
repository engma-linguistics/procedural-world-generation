---
title: "Hotspot islands are sub-cell: at level 6 (and half the time at 7) the grid shows a bank, not land"
type: task
status: needs-decision
parent: PW-001
subsystem: tectonics
effort: s
impact: med
found_by: volcanoes
blocked_by: []
relates: [PW-002]
refs: [planet/tectonics/volcanism.py, planet/zoom_volcanoes.py, viewer/index.html]
---

## Description
Hotspot vents now put their crust into a 25 km Gaussian (`volcanism.VENT_KM`), so that at level 7
(55 km cells) and level 8 consecutive vents are separate islands. A cell's elevation is a mean, though,
so at level 6 (110 km cells) a vent's cone fills only ~1/5 of its cell: a 9 km tall shield on a
−3 km floor gives the cell ~+1.5 km of relief and leaves it under the sea. Level 6 worlds therefore show
hotspot chains mostly as shallow submarine ridges (an apron at −2 km plus the cones' share), with island
cells only where several vents pile into one cell (slow plates). Measured on seed 13
(`continental_start=0.1 heat_start=2`) at 150 Myr: of the hotspot islands higher than 800 m, 12% sit on
a land cell at level 6 (22% with land within one cell) and 46% at level 7 (62%). The islands are still
there: each vent carries its own summit height (`top_m` in `meta.volcanoes`), the zoom draws them, and
the viewer's "Volcanoes" overlay marks islands and atolls on worlds.

Options:
- A. Accept it. Cell means are right; islands live in the volcano table, the overlay and the zooms.
- B. Widen the cone with the grid at coarse levels (r = max(25 km, 0.5 cell)): chains come back as
  blurred land at L6, but the vents' heights no longer match the cell means at L6 (the zoom would need
  per-level cone radii).
- C. Keep the run as is, but when a world is built, raise cells that hold an island vent to a small
  positive elevation (display only: a sub-cell maximum rather than a mean).

Lean: A, plus C if the globe looks too empty of islands (it matters for climate and rivers only a
little: these are small islands).
