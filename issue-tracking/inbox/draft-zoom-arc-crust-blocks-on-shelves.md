---
title: "Zoom: re-check arc crust on a shelf (blocky coarse-cell islands) now that arcs have a cone every ~60 km"
type: task
status: todo
parent: PW-001
subsystem: zoom
effort: s
impact: low
found_by: zoom-batch5
blocked_by: []
relates: [PW-116]
refs: [planet/zoom_volcanoes.py, planet/zoom.py, docs/review/zoom-polish/batch5.md, "world 592f2a"]
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
