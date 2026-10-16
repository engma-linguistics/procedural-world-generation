---
title: "PW-197 needs a world-wide 'land = bed > 0 or grounded ice' before finish.py can store the true bed"
type: task
status: needs-decision
parent: PW-090
subsystem: timezoom
effort: m
impact: low
found_by: small-store
blocked_by: []
relates: [PW-197, PW-189]
refs: [planet/finish.py, planet/timeline.py, planet/world.py, planet/climate.py, planet/hydrology.py, planet/tectonics/isostasy.py]
---

## Description
Looked at PW-197 (effort s) and stopped: it isn't a finish.py change. The flooring is
`isostasy.land_view`, applied in `timeline._world` (every world from a run, not only finished ones;
`meta.ice_bed_floored_cells`) and `finish._earth_world`. Storing the true bed needs every consumer
of the world's elevation to take "ice > 0" as land too: `world.finish` (`sea = elev <= 0`, currents,
the flood fill), `climate.compute` (land/sea everywhere; off-limits while PW-305 is prototyped
there), `hydrology.erode` / `rivers_and_lakes` (sea is elev <= 0: a sub-sea bed under ice would
drain to the sea), coast/waves/tides, the zoom's coastline and the viewer's sea shading. The
simulation already does this (`Simulation.land()`), so the pattern exists.
Options: (a) a world `land` mask (elevation > 0 or ice > 0) threaded through world/climate/
hydrology/coast/zoom, then drop land_view from worlds; (b) keep the floor and add a `bed` layer
for display only (zoom rock and sub-ice lakes still wrong). (a) is the real fix; ~half a day plus
a climate.py touch, so best after PW-305 lands.
