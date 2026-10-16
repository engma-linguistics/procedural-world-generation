---
id: PW-340
title: "Zoom stats: landform shares, overlay counts, knickpoints and rivers entering include the halo"
type: task
status: todo
parent: null
subsystem: zoom
effort: xs
impact: low
found_by: zoom-batch2
blocked_by: []
relates: [PW-321]
refs: [planet/zoom.py, planet/zoom_landforms.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Since PW-321 the zoom's terrain is built on the region plus a halo (`zoom.HALO_CELLS` = half a coarse cell)
and cropped before the climate. Layers, falls, lakes, deltas' mouths, volcanoes and the cell-mean stats are
on the region, but a few stats are still counted over the built area: `stats.landforms` (`lf.stats()`,
% of land per class), `stats.landform_overlay` (dunes' types, dolines, towers, springs: `lf.finish`),
`stats.landform_basins`, `stats.knickpoints`, `stats.distributary_splits`, `stats.rivers_entering`
(rivers crossing the halo's edge) and `coarse_cells` / `coarse_river_cells`. Each is off by the halo's
share (~6% of pixels at 4 km, ~25% at 1 km, ~54% at 0.5 km). Count them on the cropped pixels (a mask
argument to `lf.stats` / the overlay counters; filter knickpoints and entries to the region).

## Updates
- 2026-10-16: Created from inbox draft draft-zoom-stats-over-halo.md (found by zoom-batch2).
