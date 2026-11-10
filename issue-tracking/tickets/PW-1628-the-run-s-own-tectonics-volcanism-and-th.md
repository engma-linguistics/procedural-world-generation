---
id: PW-1628
title: The run's own tectonics, volcanism and the lineages still count every cell as the mean cell's area
type: task
status: in-progress
parent: null
milestone: later
subsystem: tectonics
effort: s
impact: low
found_by: lane263
blocked_by: []
relates: [PW-1043]
refs: ["planet/grid.py::Grid.cell_area_km2", "planet/tectonics/simulation.py::Simulation._configure", planet/tectonics/mantle.py, planet/tectonics/motion.py, planet/tectonics/volcanism.py, planet/tectonics/diag.py, planet/lineages/landuse.py, planet/lineages/history/model.py, planet/zoom/resources.py, planet/zoom/vegetation.py, planet/highlights.py]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: PW-1043 (lane 263) made rivers, lakes, island and sea sizes, ice volume and the health/export/highlight
areas add up each cell's true area (`Grid.cell_area_km2`; on L6 the cells run 0.675-1.206 of the mean). A second
group still treats every cell as the mean one: `Simulation.cell_area` (4 pi / n) weights the mantle's slab cold and
the plates' drag (`mantle.py:228,303`, `motion.py:157`) and `diag.py`'s areas; `volcanism.py:105,476` turn erupted
volume into thickness over the mean cell; the lineages' `landuse.py:171` and `history/model.py:66` (cell_mkm2), and the
zoom's `resources.py:203` / `vegetation.py:364` scale by the mean cell.

What breaks if never done: lava and ash near the grid's twelve pentagons come out up to a third thicker, or a fifth
thinner elsewhere, than their volume says; a polity's or a field's area there is off by the same; small and spread
evenly over the globe, so low impact, but each one is a wrong number someone will read as true.

Fix: read `grid.cell_area_km2` (per cell) wherever cells are added up into an area or a volume is spread over a cell;
keep the mean (`geo.cell_area_km2(n)`, now documented as the mean) only for per-cell scales. The tectonic ones move
every run's history: goldens and a fork screen (`tools/fork_screen.py`).
- [ ] no area or volume total in planet/ multiplies a cell count by the mean cell's area

## Updates
- 2026-11-10: Status todo -> in-progress. Lane 268 (857324b2, not merged): plate drag, mantle traction, volcanism volumes, diag area shares, highlights reef/mangrove km2, zoom full_px and deposit rates use true cell areas. Mean area kept on purpose in mantle slab smoothing (equal-weight basis), discharge (flow already in mean-cell units), and per-cell scales. Left: planet/lineages/ sites (brief.py:300-301, settlements.py:553, ladder.py:384, animals.py:154,350-352, trade.py:212, fuels.py:170, landuse.py:171, history/model.py:66) and diag climate means (judge/hard_bar read them; separate commit). Fork screen L6 seeds 1/2/77/3199 vs main 673436c0 with fp-null: no consistent effect (mild lower inland median on 77 and 3199). Scorecard still to run.
- 2026-11-10: Created from inbox draft draft-tectonics-volcanism-true-cell-areas.md (found by lane263).
