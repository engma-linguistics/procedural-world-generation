---
id: PW-362
title: "Zoom: re-check arc crust on a shelf (blocky coarse-cell islands) now that arcs have a cone every ~60 km"
type: task
status: done
parent: PW-001
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: zoom-batch5
blocked_by: []
relates: [PW-116]
refs: [planet/zoom_volcanoes.py, planet/zoom.py, docs/review/zoom-polish/batch5.md, "world 592f2a"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-116 (zoom batch 5) added cones between neighbouring active arc volcanoes in the zoom
(`zoom_volcanoes.arc_infill`: one every ~60 km along the chain, 0.6-0.95 of the lower neighbour's height), so a
volcanic front reads as a chain. Its other half was not re-checked: on an arc over a flooded shelf (the
"Indonesia-like" case, PW-116's description) the arc crust itself, which the run puts in the coarse cells, may
still stand as two or three blocky islands round the cones. The showcase world 592f2a has its dense active arcs
either on land (-53.4,1.23: a continental arc in mountains) or on deep floor (-57.6,135.5: islands and seamounts),
none on a shelf. Find a shelf arc on a current showcase world, zoom it at 1-2 km, and if the arc crust reads as
blocks, consider shaping the land of arc cells round the cones (e.g. the arc crust's share of a cell's mean put on
the cones' flanks and a ridge along the chain rather than spread over the cell).
- [ ] a shelf arc zoomed and looked at; blocks or not, with an image

## Updates
- 2026-10-16: Status in-progress -> done. Done (06b1157), option B: a land cell's own sea pixels take what its mean lacks (shelf round the island); fac2af mesa land p50 1334 -> 607 m. Remaining plateau: PW-383.
- 2026-10-16: Status todo -> in-progress. Small fixes batch agent started.
- 2026-10-16: Status in-progress -> todo. Coordinator 2026-10-16: lean B (keep part of a forearc cell's mean in its sea instead of the trench's depth), for a later zoom batch.
- 2026-10-16: Note to the entry above: that the summit cap flattens the mesa's top is a guess from its shape (flat at 1600-1650 m), not checked against the pass's stages.
- 2026-10-16: Stopped (zoom batch 6): re-checked, still blocky, but not the cones' doing; the fix is a design choice. Shelf arcs are rare on the current showcase worlds: active arc volcanoes over a -400..0 m floor with >= 3 sea neighbours: 592f2a / bd9a7a 1 each, fac2af (glacial lowstand, -128 m) 2. Zoomed fac2af at -1.467,36.085 (500 km @ 1 km, seed 1; image docs/review/zoom-polish/pw362_shelf.png): the volcanoes (run's and PW-116's minor cones) are clean cones and small islands; the blocks are forearc cells without cones, between the chain and the trench: cell 52473 (+194 m mean, rock 5, among -400..-600 m shelf cells and the trench's -4800 m) is a 1,900 km2 mesa, p10/p50/p90 382 / 1315 / 1631 m, flat-topped at ~1600-1650 m with ~1500 m cliffs within 2-3 px of the coast; cells 136933/71717 (+78 m) a 100 km island sloping off a 900 m western end. Cause: each coarse cell's mean is kept while its sea pixels take the interpolated shelf/trench floor, so a +194 m cell's land third must stand ~1500 m, lifted evenly (a plateau) and capped flat by the landscape pass's summit cap. Options: A) in a mixed land/sea cell put the mean's correction on the land by distance from its coast (a dome, not a mesa), for every coast (all zooms move); B) let such cells keep their mean partly in the sea (a shallower floor round the island, a shelf), i.e. take the trench's depth off the cell's sea pixels near the island; C) arc-specific: put the cells' arc crust on a ridge along the chain (the ticket's idea) - doesn't apply here, the blocks are forearc cells with no cones. Lean: B (the sea pixels next to a trench were what forced the mesa), with A as the general fallback; needs a decision since A/B touch every coast's mean keeping.
- 2026-10-16: Status todo -> in-progress. Zoom batch 6 agent started.
- 2026-10-16: Created from inbox draft draft-zoom-arc-crust-blocks-on-shelves.md (found by zoom-batch5).
