---
id: PW-352
title: "Humid subtropical summers run 4-6 C too warm (SE China, SE USA, Pampas): any physical shower trigger then dries them"
type: task
status: todo
parent: PW-013
milestone: null
subsystem: climate
effort: m
impact: med
found_by: moisture-budget
blocked_by: []
relates: [PW-015, PW-305]
refs: [planet/climate.py, tools/earth_check.py, tools/moisture_budget.py, docs/proposals/moisture_transport.md, docs/review/audit/pw015-rain.md]
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
- 2026-10-16: Merged inbox draft draft-east-coast-summers-first-pass.md ("Humid east coasts' summers are warm in the first-pass air temperatures, not from the evaporative split (PW-352 diagnosis); PW-015 stage 3 waits on it", found by pw015-rain).
  For PW-352 (probably `--merge-into PW-352`). Earth L6 on the PW-015 branch (stages 1-2), warmest month:
  first pass (`_air_temps`, before the rain) / final (`_land_finish`) / NCEP, with the summer's AET/PET:
  
  | region | first | final | NCEP | AET/PET |
  |---|---|---|---|---|
  | NE USA | 28.4 | 27.3 | 21.3 | 0.90 |
  | SE USA | 30.6 | 31.0 | 25.3 | 0.23 |
  | SE China | 30.2 | 29.1 | 24.5 | 0.71 |
  | E Australia | 29.6 | 29.9 | 23.7 | 0.26 |
  | Pampas | 30.9 | 31.5 | 25.2 | 0.17 |
  | W Europe | 19.1 | 18.2 | 18.0 | 0.74 |
  | Great Plains | 24.9 | 24.5 | 25.0 | 0.59 |
  | Sahara / Arabia | 31.0 / 29.1 | 31.9 / 30.1 | 31.5 / 33.9 | 0.05 / 0.09 |
  
  Over all 20-50 deg land, binned by summer AET/PET, the final warm bias is only +0.2 C (0-0.2), +1.6..+1.9
  (0.2-1.0). So a stronger evaporative cooling (a Bowen-ratio split: ~1 day of sensible heat into a 1.5 km
  layer gives ~5-7 C per unit of evaporative fraction in a hot summer) would take ~2 C off the humid land on
  average, but not the east coasts' +4.6..+6 C, which are already there in the first pass: the air carried
  onto the east coasts in summer is the continent's (continentality, the summer wind), not the subtropical
  highs' maritime air. Wet NE USA (AET/PET 0.9) is +6 C. Likely the same air model as PW-026 (winter maritime
  air inland), from the summer side.
  
  Why it blocks PW-015 stage 3: the humid-column shower gate (Bretherton et al. 2004's exp(15.6 r)) and the
  air-mass trigger reference both dry the humid subtropics while they are this warm (q/qs is low where qs is
  too high): with the gate, SE USA 277 -> 110 mm, SE China 1163 -> 788 (obs 1328, 1462), Koppen group 70.3
  -> 69.0. Also: the kernel sees only the first-pass temperatures (the land finish comes after the rain);
  a fix should reach the rain's inputs too (e.g. update the season inputs once mid-kernel from its own rain).
  - [ ] east-coast warmest months (NE USA, SE USA, SE China, E Australia, Pampas) within ~2 C of NCEP, dry
    interiors not warmer
  - [ ] then PW-015 stage 3 (docs/proposals/moisture_transport.md section 8)
- 2026-10-16: Created from inbox draft draft-humid-subtropics-summers-too-warm.md (found by moisture-budget).
