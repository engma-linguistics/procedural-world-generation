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
- 2026-11-10: Lane 268b: merged main 1090b13f into the branch (clean; goldens unchanged and passing; not-slow suite 1975 passed, 15 skipped at c06326de). Scorecard (tools/scorecard.py --jobs 2 --threads 4, line c06326de in docs/scorecard.jsonl; the sim code it runs is lane 268's 857324b2 plus main) against main's latest line b7773291 (lane 263, PW-1043; no sim code changed on main since): Earth identical (group 71.4%, exact 37.3%, rain 1050 mm, log corr 0.718). Seed 1: land 32.9 -> 32.1%, dry 22.0 -> 34.2%, ice 1.8 -> 0.9%, largest 11.9 -> 7.9%, shelf 2.4 -> 3.0%, gt4km 3.22 -> 2.16%, trees 48.0 -> 40.9%, volume x0.981 -> x0.993. Seed 2: land 33.3 -> 34.0%, dry 22.9 -> 29.8%, ice 3.5 -> 2.1%, largest 9.7 -> 13.2%, ocean age 47.8 -> 73.9 Myr, volume x1.029 -> x1.006. Against the spread of the 11 scorecard lines before it (ca715232..b7773291), the measures outside are seed 1 dry 34.2% (16.1-30.6), plate_max 16.4% (17.8-49.3), shelf 3.0% (1.2-2.8); seed 2 dry 29.8% (15.9-29.7), masses 22 (6-21), land range 30.6-36.7% (30.7-32.7 / 34.2-36.5), plate_max_max 39.7% (41.2-63.1), all at the edges. Dry rose on both seeds, so seeds 3 and 4 were run paired (tools/scorecard.py world_scores, L6 1 Gyr, main cc5b85af in a scratch worktree vs this branch): dry 26.2 -> 16.8% (seed 3), 21.4 -> 20.2% (seed 4), so dry -9.4/-1.2 there against +12.2/+6.9 on seeds 1/2, no consistent sign; ice 0.6 -> 7.7%, 5.7 -> 3.6%; land 34.5 -> 34.9%, 35.3 -> 32.8%; volume x1.003 -> x1.014, x1.036 -> x1.003. No hard failure on any of the four seeds (none frozen or boiled, ice <= 7.7%, land 32-35%, crust volume within 1.5%; CO2 not in the scorecard). Read with lane 268's fork screen (L6 seeds 1/2/77/3199, no consistent effect; inland-drainage median mildly lower on 77 and 3199): no measurable effect beyond the run's chaos; the branch is ready to merge for the tectonics/volcanism/diag/highlights/zoom part. Left open for a later lane: the planet/lineages/ sites listed above and the diag climate means.
- 2026-11-10: Status todo -> in-progress. Lane 268 (857324b2, not merged): plate drag, mantle traction, volcanism volumes, diag area shares, highlights reef/mangrove km2, zoom full_px and deposit rates use true cell areas. Mean area kept on purpose in mantle slab smoothing (equal-weight basis), discharge (flow already in mean-cell units), and per-cell scales. Left: planet/lineages/ sites (brief.py:300-301, settlements.py:553, ladder.py:384, animals.py:154,350-352, trade.py:212, fuels.py:170, landuse.py:171, history/model.py:66) and diag climate means (judge/hard_bar read them; separate commit). Fork screen L6 seeds 1/2/77/3199 vs main 673436c0 with fp-null: no consistent effect (mild lower inland median on 77 and 3199). Scorecard still to run.
- 2026-11-10: Created from inbox draft draft-tectonics-volcanism-true-cell-areas.md (found by lane263).
