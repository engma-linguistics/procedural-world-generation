---
id: PW-307
title: PW-197 needs a world-wide 'land = bed > 0 or grounded ice' before finish.py can store the true bed
type: task
status: done
parent: PW-090
milestone: null
subsystem: timezoom
effort: m
impact: low
found_by: small-store
blocked_by: []
relates: [PW-197, PW-189]
refs: [planet/finish.py, planet/timeline.py, planet/world.py, planet/climate.py, planet/hydrology.py, planet/tectonics/isostasy.py]
created: 2026-10-15
updated: 2026-10-16
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

## Updates
- 2026-10-16: Status in-progress -> done. Done (e4c341a): geo.is_land/world_land (elevation > 0 or grounded ice) through world.finish, climate.compute, hydrology, coast, coastal life, satellite, vegetation, highlights, viewer ('bed under ice' layer); worlds store the true bed (land_view dropped; isostasy.grounded). No-ice worlds bit-identical; seed 11 @ 236 Myr: 298 ice cells on a sub-sea bed, rivers/lakes unchanged.
- 2026-10-16: Status todo -> in-progress. Agent started (option a; lands before the rain rework per the moisture proposal's decision 6), with PW-197.
- 2026-10-15: Status needs-decision -> todo. Owner 2026-10-15: option (a), the world land mask, but later. PW-013 decides the order (before, during or after it), since both touch climate.compute.
- 2026-10-15: Created from inbox draft draft-world-grounded-ice-land.md (found by small-store).
