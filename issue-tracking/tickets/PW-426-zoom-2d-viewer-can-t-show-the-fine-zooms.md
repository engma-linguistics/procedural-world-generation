---
id: PW-426
title: Zoom 2D viewer can't show the fine zooms' valley floors (valley_floor, floor_m)
type: task
status: done
parent: null
milestone: null
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
- 2026-10-16: Done (viewer lane). zoom.html: "Valley floor" (categorical, legend floodplain / meander belt /
  channel on the floor with km² each) and "Floor height" (floor_m on the floors only, ramp over the zoom's
  floor range, hillshade elsewhere); hover row "valley floor: <class>, <m>". Hidden on zooms without the
  layers (NEEDS), so on coarse zooms. The 3D view takes the same picker. Checked on a fresh fine zoom of
  369394 at -2.41, -7.59 in a scratch data root (97.6 km² of floors) in 2D and 3D.
