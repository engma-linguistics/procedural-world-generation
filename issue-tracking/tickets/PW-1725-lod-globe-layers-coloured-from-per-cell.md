---
id: PW-1725
title: "LOD globe: layers coloured from per-cell tables (human use, resources, coasts, peoples) show only the satellite view on detail tiles"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: viewer
effort: m
impact: med
found_by: lane301
blocked_by: []
relates: [PW-1673, PW-1688]
refs: ["viewer/globe/layers.js::tileLayer", "viewer/globe/lodtiles.js::valuesTexture", "viewer/globe/lodtiles.js::legendNote", viewer/globe/colours.js, docs/review/zoom/lod-plan-v2.md, "world dba204"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Diving into the globe now keeps the active layer on the detail tiles when the zoom has the same
layer (elevation, temperature, rain, biome, vegetation, soils, climate, landforms, tree cover and the other plain
ramps and classes: `layers.js::tileLayer`). Layers that the globe colours from per-cell tables rather than from one
value per place (the human-use group, resources, coast scores, peoples and the body/animal/crop families, the plant
type) can't be coloured that way: on the tiles they fall back to the satellite view, and a line under the legend says
so (`lodtiles.js::legendNote`). If never done, someone looking at a peoples or resource map loses it below ~4,000 km:
the map turns into the satellite picture exactly where they zoom in to look closer.

What to try, per group: the zooms already carry several of these as their own layers (`harbour`, `pass`, `fertile`,
`fresh_water`, `river_nav`, `grazing`, `foraging`, `timber`, `fuel`, `travel`, `hazards`, `coast_type`); give each a
tile colouring that reads the tile's values with the globe's swatches. Peoples, polities and families have no zoom
twin: draw the globe cell's colour on the tile instead (sample the globe cell under each tile pixel; a lookup by
`nearestCellU`), which at least keeps the map.
- [ ] the human-use layers with a zoom twin drawn on tiles in the globe's colours
- [ ] peoples/polities layers keep their colours on tiles (the cell's colour), no satellite fallback

## Updates
- 2026-11-11: Created from inbox draft draft-lod-tiles-table-coloured-layers.md (found by lane301).
