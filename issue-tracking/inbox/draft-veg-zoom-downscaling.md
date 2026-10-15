---
title: "Vegetation in the regional zoom (PW-187 step 5): per-pixel equilibrium, terrain light and water, river water, fire mosaic"
type: story
status: todo
parent: PW-184
subsystem: zoom
effort: m
impact: high
found_by: veg
blocked_by: []
relates: [PW-187, PW-196, PW-139]
refs: [planet/vegetation.py, planet/zoom.py, docs/proposals/vegetation.md]
---

## Description
Step 5 of docs/proposals/vegetation.md section 9.1 (section 3.7). Worlds now carry the vegetation (`vegetation`, `tree_cover`, `veg_<PFT>` for 19 PFTs, `fire_return`, `stand_age`, `flooded`); the zoom still classifies pixels with `climate.biomes` (Whittaker) at zoom.py ~l.2359. Notes from building steps 1-4:
- `vegetation.model()` takes per-cell arrays and a grid only for the neighbour spread and the relief/flooded helpers; a raster version needs: months from the zoom's lapse-corrected temperature and per-pixel half-year rain (PW-139 would give the seasons), the zoom's own relief for the soil depth, and a pixel neighbourhood (or diff=0).
- Cost: world mode is ~0.2 s per 15k land cells at L6 (potential NPP ~60% of it). 250k pixels ~3-4 s; compute potential NPP on a 4x coarser lattice and only the bucket and wetness per pixel (proposal section 6).
- Warm-start each pixel from the coarse cell's fractions (history: forest vs savanna) and pull the pixel means back to the cell's fractions except where the terrain clearly differs.
- River water: pixels next to rivers should get the river's water in the bucket; this is what makes gallery forest and oasis woodland (named type 18 never appears at cell scale: a 55-110 km cell is too coarse for a river strip).
- Fire mosaic: sample stand age from the cell's exponential distribution (mean `stand_age`) with planet-fixed 3D noise, so overlapping zooms agree.
- Zoom layers per decision 9A: vegetation, tree_cover, cover, lai, canopy_height, npp, fire_return; viewer zoom.html layers and hover.
