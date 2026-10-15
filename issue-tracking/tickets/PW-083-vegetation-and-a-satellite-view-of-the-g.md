---
id: PW-083
title: Vegetation and a 'satellite view' of the globe and zooms
type: task
status: todo
parent: null
subsystem: viewer
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [viewer/index.html, viewer/zoom.html, planet/zoom.py, planet/zoom_vegetation.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Owner backlog: vegetation, and eventually a "satellite view" (true-colour rendering from biome, rock,
snow, water) of the globe and zooms. "Not yet": pick up after PW-005 and PW-001.

## Updates
- 2026-10-15: Merged inbox draft draft-zoom-veg-satellite-preview.md ("Satellite view in zooms (PW-083): compute the colours at build time, where the per-PFT fractions exist", found by vegzoom).
  Notes for PW-083 on the zoom side (to merge into it). Zooms store only the vegetation summary layers (decision 9A: vegetation, tree_cover, plant_cover, lai, canopy_height, npp, fire_return); the per-PFT fractions exist only inside zoom_vegetation.compute (or recomputed by zoom_vegetation.fractions in ~5 s). A satellite colour (sum of fraction x PFT colour x greenness, bare ground by surface rock, snow and ice, water) is therefore best computed in zoom.build and stored, either as the preview.png (today tinted by rain and height: `zoom.tint`, so gallery forests, treelines and mires only show on the Vegetation / Tree cover layers) or as a small RGB layer per season (July / January from lai and the PFTs' leaf habits), which zoom.html can draw as a layer. The globe's satellite view needs the same colour function on the world's veg_<PFT> layers; share it (vegetation.py) so both match.
  - [ ] zoom preview.png (and/or a satellite layer) coloured from the pixel's PFT mix
- 2026-10-15: Owner (2026-10-15): wanted. Impact raised to high. The vegetation layers now exist (PFT fractions, lai_jul/jan); scheduled after the vegetation-in-zooms merge (PW-214) so globe and zooms get it together.
- 2026-10-14: Rescoped: the 'satellite view' only; vegetation itself is PW-187, which this waits for.
- 2026-10-14: Migrated from plan_next@bdc967f Backlog (owner notes 2026-10-14).
