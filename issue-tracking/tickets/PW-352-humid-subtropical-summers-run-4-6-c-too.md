---
id: PW-352
title: "Humid subtropical summers run 4-6 C too warm (SE China, SE USA, Pampas): any physical shower trigger then dries them"
type: task
status: todo
parent: PW-013
subsystem: climate
effort: m
impact: med
found_by: moisture-budget
blocked_by: []
relates: [PW-015, PW-305]
refs: [planet/climate.py, tools/earth_check.py, tools/moisture_budget.py, docs/proposals/moisture_transport.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Earth L6 (earth_check regions, warmest month model / observed): SE China 29.2 vs 24.5 C, SE USA 29.6 vs 25.3, Pampas 30.3 vs 25.1 (PW-305's numbers, still so on main cc431ed). Both trigger fixes tried for the dry interiors hit these regions:
- PW-305's steady mixed layer (E1 deep variant): SE China 1134 -> 472 mm, SE USA 1346 -> 518. The hot summers give a large PET - AET, a deep dry layer, fewer showers and drier ground: a runaway.
- PW-015's prototype air-mass reference aloft (docs/proposals/moisture_transport.md §4): SE USA 1158 -> 546 mm, SE China 1311 -> 895. The over-warm air mass raises the reference and stabilises the column.

So the summers have to be right before the trigger can be made physical (proposal decision 3: "no temporary fixes"). Where the heat comes from is open:
- The summer evaporative cooling is capped at 1.5 C (`evap_cool`, `evap_r`).
- The continentality swing is the same for humid and dry interiors.
- There is no cloud shading (clouds are diagnostic, PW-163). Real summers there are cloudy, with surface latent heat ~100 W/m2.

Try the summer's actual/potential evaporation as a proper surface energy split (Bowen ratio) before reaching for clouds.
- [ ] SE China, SE USA, Pampas warmest month within ~2 C of NCEP, with dry interiors not warmer
- [ ] re-run PW-015 step 3's trigger on top

## Updates
- 2026-10-16: Created from inbox draft draft-humid-subtropics-summers-too-warm.md (found by moisture-budget).
