---
id: PW-374
title: "Zoom vegetation: straight, axis-aligned edges (rectangular patches) and a July/January jump at the equator"
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: med
found_by: iceage-showcase
blocked_by: []
relates: [PW-214, PW-139]
refs: [planet/zoom_vegetation.py, planet/zoom.py, "zoom 369394", "zoom 634f6c", "world bcd6c8"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Two zooms of the ice-age showcase world bcd6c8 (run 2c2810 @ 536 Myr, time zoom 98ee98 @ 614 kyr) show vegetation patches with ruler-straight edges along the pixel rows and columns, visible on the satellite, vegetation, tree cover, NPP, LAI, plant cover, fire return and soil carbon layers, while the terrain, annual temperature and rain are smooth across them.

- **Zoom 634f6c** (-9.4, 110.3, 500 km @ 1 km): a rectangle with a vertical edge at column ~372 running over rows 13-478 (101 rows with a tree-cover jump > 15 points; 41 points mean jump against ~8 between neighbouring columns) and a horizontal edge at row ~205. Only vegetation-derived layers jump (canopy height, plant cover, tree cover, vegetation, peat); temperature, rain and July/January rain do not.
- **Zoom 369394** (-1.2, -6.7, 1000 km @ 2 km): a rectangle with edges at row ~182 and column ~81 (fire return 6680 -> 0 years and tree cover 38 -> 0 % across one pixel at column 81, climate smooth there).

Hypothesis (not checked): `V.equilibrium` seeds types from their 4-neighbours on the pixel grid (`_neighbours`) for a fixed number of steps, so a type invading from a seed spreads as a square/diamond front and stops where the steps run out; bistable ground (savanna/forest, grass/shrub) keeps the front's straight edges.

Separately, at the equator in 369394 `temperature_jul` and `temperature_jan` jump by ~13.9 °C between rows 181 and 182: `zoom.py` builds them as the warmest / coldest month by hemisphere (`np.where(north, t_warm, t_cold)`), so they swap at latitude 0, and `zoom_vegetation` takes the summer half-year by hemisphere (`summer_half = np.where(north, ...)`). The horizontal seam of 369394 sits on that row, so part of it may be this swap rather than the front.

## Acceptance
- No axis-aligned vegetation edges on 634f6c and 369394 rebuilt (tree cover jumps across one pixel no more common along any single row or column than elsewhere).
- July / January temperature continuous across the equator in a zoom that straddles it.

## Updates
- 2026-10-16: Created from inbox draft draft-zoom-vegetation-straight-edges.md (found by iceage-showcase).
