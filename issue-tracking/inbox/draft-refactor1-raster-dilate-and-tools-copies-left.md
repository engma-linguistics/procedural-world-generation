---
title: Several mask-grow (dilate) copies and the tools' map-painting helpers are still separate
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: m
impact: low
found_by: refactor-lane-59
blocked_by: []
relates: [PW-1048, PW-1049]
refs: [planet/raster.py, planet/zoom/regional.py, planet/zoom/landforms.py, planet/zoom/coast.py, planet/resources.py, planet/lineages/history/dispersal.py, planet/highlights.py, tools/veg_check.py, tools/soil_check.py, tools/zoom_soil_check.py, tools/earth_check.py, tools/resources_check.py]
---

## Description
In plain words. Refactor 1 started `planet/raster.py` with one `box_mean` (three identical zoom copies merged). The "grow a mask by N pixels" copies were not merged: two (`regional._dilate`, `landforms._dilate`) wrap around the map edge and the third (`zoom/coast._dilate`) does not, so merging changes outputs (PW-1048, which also wants a non-wrapping `dilate` and one `shift`). The grid-level dilates (`resources._dilate`, `dispersal._dilate`, `highlights._Ctx.dilate`, `timezoom/kernels.dilate`) walk neighbour rings and could become one `Grid.dilate(mask, rings)`; they were left because the time-zoom one is in the ice lane's file and the others have not been proven identical.

The tools were left to the tools lane: `_rgb` (veg_check, soil_check, zoom_soil_check), `_hex`/`_ramp` (earth_check, resources_check) and the panel-stacking `maps_png` shape can now use `planet.images.hex_rgb` and `images.ramp_colour`; `earth_check.wmean` and `climate_bias._wm` are one area-weighted mean.

- [ ] one non-wrapping `raster.dilate` and `raster.shift` (PW-1048), then the zoom callers
- [ ] `Grid.dilate`, after proving each grid copy gives the same rings
- [ ] tools switch to `images.hex_rgb`, `images.ramp_colour`, one `geo.area_mean`
