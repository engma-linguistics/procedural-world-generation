---
id: PW-1701
title: "A level-2 tile of dba204 (py.1.1/2/1/5) fails to build: vegetation's is_land is handed the tile's land pixels, which are no sphere grid"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: s
impact: high
found_by: lane294
blocked_by: []
relates: [PW-1690, PW-1689]
refs: ["planet/vegetation.py::classify", "planet/geo.py::is_land", "planet/geo.py::_grid_of", "planet/zoom/vegetation.py::compute", "planet/zoom/fine.py::build", "planet/zoom/lod_build.py::tile", planet/tiles.py, "world dba204", "tile py.1.1/2/1/5"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** One of the first fifteen detail tiles the on-demand globe built on world dba204 crashed, every time:
tile `py.1.1/2/1/5` (cell py.1.1, level 2, 500 km at 1 km, built from the cell's 4 km section). The globe then shows the
blurry level-1 picture there for good, and nothing finer under it can be built (the tile service marks its children
"blocked"). If this is never done, some spots on most worlds can never be zoomed into.

Reproduce (a scratch data root holding dba204 and the py.1.1 4 km section; the build takes ~20 s):

    PLANET_DATA=<root> uv run python -c "from planet.zoom import lod_build as LB; LB.tile('dba204', 'py.1.1/2/1/5')"

    fine.py::build -> zoom/vegetation.py::compute (ZVG.compute) -> vegetation.py::classify:
        put(~is_land(elev, ice), 0)
    geo.py::is_land -> _grid_of(249929): ValueError "is_land: 249929 cells is no sphere grid; pass grid="

`classify` is given the tile's land pixels (249,929 of 250,000 here), not a sphere grid's cells. `is_land` only needs a
grid when some of them are at or below sea level (a land pixel lying below the sea: a depression or a pixel the
coast calls land), which is why most tiles build and this one doesn't. The sea/land call was already made by the
zoom (its `water` layer), so the zoom's caller should hand classify that land mask (or classify should take one),
not recompute it on a grid it doesn't have. Not fixed by lane 294: planet/zoom was another lane's this round.
- [ ] `py.1.1/2/1/5` of dba204 builds; a synthetic tile with a land pixel below sea level builds (test)

## Updates
- 2026-11-11: Created from inbox draft draft-lod-tile-build-crashes-in-vegetation-is-land.md (found by lane294).
