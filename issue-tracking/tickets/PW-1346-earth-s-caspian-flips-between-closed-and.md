---
id: PW-1346
title: Earth's Caspian flips between closed and open basin with GPCC rain on unrelated climate changes
type: task
status: todo
parent: null
milestone: v2
subsystem: hydrology
effort: s
impact: low
found_by: lane126
blocked_by: []
relates: [PW-358, PW-1336]
refs: [tools/earth_check.py, "planet/hydrology.py::rivers_and_lakes", "planet/climate.py::open_water_evap", docs/review/base-climate/tropical-cloud/round1.md, docs/review/base-climate/tropical-cloud/ec.sh, data/earth/hydrosheds_L7.npz]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: earth_check's "known closed basins" table, with GPCC rain, shows the Caspian as closed on main,
open with lane 126's cloud gate, closed again with the split changes, and open again with the lake change. Its own lake
evaporation hardly moves (1328 vs 1323 mm/yr), so the balance there must be within a few percent of overflowing.
With the model's own rain it stays closed (73 cells) on every arm.

Why it matters: a basin this close to the edge makes earth_check's closed-basin line flip on unrelated changes, and a
reviewer can read noise as a regression.

Try: print the Caspian's inflow / evaporation ratio in earth_check. If it's within ~5% of 1, note it as marginal in
the table rather than as pass/fail. Or check whether the Volga's catchment rain (GPCC) is regridded right at L7.
- [ ] earth_check marks marginal basins; the Caspian's ratio is reported

## Updates
- 2026-11-02: Created from inbox draft draft-caspian-closed-open-knife-edge.md (found by lane126).
