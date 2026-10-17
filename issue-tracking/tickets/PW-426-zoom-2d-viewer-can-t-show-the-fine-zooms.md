---
id: PW-426
title: Zoom 2D viewer can't show the fine zooms' valley floors (valley_floor, floor_m)
type: task
status: todo
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: pw412
blocked_by: []
relates: [PW-412, PW-416]
refs: [viewer/zoom.html, "planet/zoom.py LAYER_DOC"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-412 adds two layers to fine zooms:
- `valley_floor`: an enum. 0 none, 1 floodplain, 2 meander belt, 3 the channel on the floor.
- `floor_m`: the floor's surface in m.

`viewer/zoom.html` lists its layers by hand (the layer list near line 170, CATEGORICAL near line 182, the legends near line 850), so neither layer can be picked.

To do:
- Add `valley_floor` as a categorical layer with a small legend: floor, belt, channel.
- Optionally add `floor_m` as a continuous layer, shown only where the floor is.

Both are absent on coarse zooms, so hide them there, as for other fine-only layers.

## Updates
- 2026-10-16: Created from inbox draft draft-viewer-valley-floor-layer.md (found by pw412).
