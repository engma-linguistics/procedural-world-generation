---
title: The carbon cycle's source and sink and the ice sheets' budgets still add up cells as if all were the mean cell
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: s
impact: low
found_by: lane268
blocked_by: []
relates: [PW-1043, PW-995]
refs: ["planet/tectonics/earth.py::global_temperature", "planet/tectonics/earth.py::weathering", "planet/tectonics/earth.py::ablation_zone", "planet/grid.py::Grid.cell_area_km2", "planet/grid.py::Grid.area_weight", tools/fork_screen.py]
---

## Description
In plain words: PW-1043 and PW-1628 made river flow, lakes, ice volume, plate drag, lava thickness and the
highlights' areas use each cell's true area (on L6 the cells run 0.675-1.206 of the mean). Lane 268 found a third
group that PW-1628's list did not name, all in `planet/tectonics/earth.py`, where per-cell amounts are summed as if
every cell were the mean one:
- the CO2 sink (`global_temperature`): `sink_cells.sum()` (weathering supply x climate x plants per cell, a depth: a volume needs x area);
- the CO2 source: `growth.sum()` (arc crust growth per cell) and `plume.sum()` (plume melt per cell), and `newc`
  (a count of new ocean-floor cells);
- the ice sheets' budgets in `ablation_zone` (`np.bincount(k, weights=smb - calve)` twice, ~lines 1149 and 1166):
  m/yr of ice per cell summed over a sheet, which decides which margin cells a sheet can keep.

What breaks if never done: a sheet or a weathering belt near one of the grid's twelve pentagons counts its cells up
to a third too big or a fifth too small; a sheet's keep-or-drop decision there is off by the same. The carbon terms
are learnt against references (`sim.ref_*`), so a uniform factor cancels; only the non-uniform part moves anything,
so the effect is small, but these are budgets a reader will take as true.

Fix: weight each sum by `grid.area_weight` (mean 1, so the references keep their scale). It moves every run's
history: goldens, scorecard, and a fork screen against main's spread and the fp-null (docs/coordination.md
"Forked screens"). The ice-sheet part touches PW-470's parked ice-age physics: check with that epic first.
- [ ] no carbon-cycle or ice-budget total in earth.py adds per-cell depths or rates without each cell's area
