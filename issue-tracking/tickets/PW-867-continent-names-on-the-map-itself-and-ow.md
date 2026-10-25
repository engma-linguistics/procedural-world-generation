---
id: PW-867
title: Continent names on the map itself, and owner-given names (Jangwa) that override the generated ones
type: task
status: done
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: fun-lane-26
blocked_by: []
relates: [PW-853]
refs: [planet/names.py, planet/world.py, viewer/index.html, viewer/lineages.html]
created: 2026-10-25
updated: 2026-10-25
---

## Description
PW-853 stores generated landmass names in the world summary (`summary.landmasses[].name`, new worlds) and the peoples' history reads the same names (`names.landmass_names(seed, n)`), shown in the viewer's landmass lines and the lineages text. Left over: (1) the names are not drawn on the map/globe (a label per continent at its centre, `center_lat/lon` is in the summary); (2) the owner wants to give his own name (Jangwa, a vaguely Africa-like continent from an earlier campaign): a per-world `names` override stored beside the summary (`planet name world:<id> A=Jangwa`), applied by the viewer and by the lineages; (3) worlds made before PW-853 (2a7385) keep letters in their stored summary, while the lineages show generated names for them: re-save or a `planet rename` for old worlds.
- [ ] labels on the globe/map
- [ ] `planet name` override stored with the world, read by the lineages' `Crossings`

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 27.
- 2026-10-25: Created from inbox draft draft-continent-names-on-the-map-and-owner-names.md (found by fun-lane-26).
- 2026-10-25: (fun-lane-27) Done. (1) Labels: an Overlays checkbox "Continent names" (default on, `?lmNames=0`) draws a label at each continent's centre on the globe, the live map and the projected maps (`buildLandmassNames`, `lmGroup`; projmap.js takes a label's own css height, `userData.px`). A world uses its summary's names; a peoples run uses its history's `called` names (older runs without them show no label). (2) `planet name <world> A=Jangwa` stores the owner's names in `worlds/names/<id>.json` (A = the largest landmass, B the next...; `A=` clears one; no arguments lists; `--generated` writes the generated names down). `names.landmass_names(seed, n, overrides)`, `Crossings(..., overrides)` and `recent.Pass.world_names` carry them into the peoples' history, so runs made afterwards say Jangwa; the viewer replaces the summary's names with them. The file is deleted with the world and swept as an orphan. (3) Old worlds: `planet name <id> --generated` fixes their letters (done for 2a7385: its names file now holds the generated Hizam, Talatos, Luki...). Peoples runs made before this keep the names they were made with. Tests: tests/test_lineages.py (override, CLI, delete).
