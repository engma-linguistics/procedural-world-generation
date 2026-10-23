---
title: "Zoom shore forms: flats too coarse at 2 km/px, wave direction from the wind, one lowstand, no cliff terrain"
type: task
status: todo
parent: PW-097
milestone: v2
subsystem: coast
effort: m
impact: low
found_by: polish1
blocked_by: []
relates: [PW-621, PW-097]
refs: [planet/zoom_shoreforms.py, planet/zoom_coast.py, docs/review/polish/polish-1.md, "zoom bc40a3", "zoom 9d7c44"]
---

## Description
The polish1 lane built `zoom_shoreforms.py` (PW-621): spits by longshore drift, beach-ridge plains, tidal flats
with D8 channels and drowned lowstand reefs, as the zoom layer `shore_form`. What is still missing:
- **Tidal flats at 2-4 km/px** are a 2-4 px fringe, and their channels are short stubs (zoom bc40a3: 17100 km2
  of flats, 1532 km2 of channels). There are two causes:
  - the zoom's near-shore bathymetry is interpolated from 60 km cells, so the flats have to build over floor
    shallower than 25 m;
  - real creek networks are finer than a pixel.
  Try them on a 1 km zoom with big tides, or on a fine zoom; or let the fine zoom carve channels into its terrain.
- **Wave direction**: the drift uses the world's annual wind as the wave direction. coast.py's wave rays know
  where the power comes from (swell from distant storms). Storing a mean wave direction per sea cell
  (`wave_dir`) would make the drift right on swell coasts, such as the westerlies' swell on west-facing coasts.
- **Drowned reefs** use the single lowstand `meta.sea_level_change_m`, not the time zoom's curve per frame.
  There are no raised reef terraces on uplifting arcs.
- **Cliffs as terrain** (a steep step at cliff shores, behind `--terrain`) are not built.
- [ ] channels form branching networks on a 1 km macrotidal zoom
- [ ] drift follows a stored wave direction where swell dominates
