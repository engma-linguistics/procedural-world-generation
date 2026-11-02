---
id: PW-1374
title: "A people's shown density counts shared cells as wholly its own: report people per km2 it fills (Q1 A)"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane 137 (density ladder check a)
blocked_by: []
relates: [PW-1275, PW-1350]
refs: ["planet/lineages/ladder.py::Ladder.refresh (h.dens: mean over held cells)", "planet/lineages/ladder.py::Ladder.mean_density", "planet/lineages/ladder.py::Ladder.by_rung", "planet/lineages/history/peoples.py::population", "tools/peoples_robust.py::measure (density, ways)", planet/lineages/techtree.py, planet/lineages/compose.py, viewer/lineages.html, docs/review/peoples/density-ladder/build.md, docs/review/peoples/density-ladder/fill_probe.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the land itself holds about what the ladder says (on dnd seed 7, world 4360a3, people per km2 of peopled land is 0.9x
the ladder's number there; plough-led cells 14.4 against 16.1, irrigation-led 33 against 33). But each people's own "density" number,
shown in the workbench and saved with the run, is its people over every cell it is present in, and a cell is shared by ~2 peoples
(presences per cell sum to 0.83 on average, mean 1.9 peoples). So each people's number comes out at ~0.4x its rung, which reads as
if the ladder were 2.5x too low. It is not: the rung is per km2 the people fills.

Lane 137 chose to keep the rungs as they are (no calibration: dividing by the mean presence would pack every shared cell at ~2x the
sourced densities). What remains is the number shown:
- [ ] `h.dens[k]` / `Ladder.mean_density` / `tools/peoples_robust.py::measure` report people over the presence-weighted area
      (sum of presence x cell area), so a people's number reads against its rung directly
- [ ] check the readers of `h.dens` (growth's eras, compose's head weighting, techtree `density_x` with dens_ref 10, saved demography)
      before changing it inside the history; the workbench label says "per km2 it fills"

## Updates
- 2026-11-02: Created from inbox draft draft-ladder-density-per-filled-land.md (found by lane 137 (density ladder check a)).
