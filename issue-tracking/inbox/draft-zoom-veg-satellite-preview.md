---
title: "Satellite view in zooms (PW-083): compute the colours at build time, where the per-PFT fractions exist"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: med
found_by: vegzoom
blocked_by: []
relates: [PW-083, PW-214]
refs: [planet/zoom.py, planet/zoom_vegetation.py, viewer/zoom.html]
---

## Description
Notes for PW-083 on the zoom side (to merge into it). Zooms store only the vegetation summary layers (decision 9A: vegetation, tree_cover, plant_cover, lai, canopy_height, npp, fire_return); the per-PFT fractions exist only inside zoom_vegetation.compute (or recomputed by zoom_vegetation.fractions in ~5 s). A satellite colour (sum of fraction x PFT colour x greenness, bare ground by surface rock, snow and ice, water) is therefore best computed in zoom.build and stored, either as the preview.png (today tinted by rain and height: `zoom.tint`, so gallery forests, treelines and mires only show on the Vegetation / Tree cover layers) or as a small RGB layer per season (July / January from lai and the PFTs' leaf habits), which zoom.html can draw as a layer. The globe's satellite view needs the same colour function on the world's veg_<PFT> layers; share it (vegetation.py) so both match.
- [ ] zoom preview.png (and/or a satellite layer) coloured from the pixel's PFT mix
