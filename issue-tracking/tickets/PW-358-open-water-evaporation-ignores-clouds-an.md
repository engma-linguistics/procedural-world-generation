---
id: PW-358
title: Open-water evaporation ignores clouds and humidity, so wet basins stay closed and hold giant lakes
type: task
status: in-progress
parent: null
subsystem: climate
effort: s
impact: med
found_by: basins-lakes
blocked_by: []
relates: [PW-300, PW-054]
refs: [planet/climate.py, planet/hydrology.py, docs/review/audit/basins-lakes.md, docs/review/health-rain-before/, docs/review/health-rain-after/, planet/zoom.py, planet/world.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`climate.water_balance` sets `lake_evap = open_water (1.2) x pet`, and `pet` is Oudin's formula on
top-of-atmosphere radiation and temperature: it doesn't see clouds or humidity. In humid climates that
gives open water ~1800-2100 mm/yr (L6 health runs: seed 77 @480 Myr 2033 mm at 26.8 C and P 1455 mm;
seed 3199 @52 Myr 1811 mm at 23.4 C, P 1177 mm), where humid tropical lakes and floodplains evaporate
~1300-1600 mm (Lake Victoria ~1500, Amazon floodplain lakes ~1300-1400). With land evaporation (aet) at
~800-900 mm there, a lake's extra loss (lake_evap - aet, what `hydrology.lakes` balances against inflow) is
~1000-1100 mm instead of a few hundred.

Why it matters (PW-300): giant run-frame lakes (1-7 Mkm2) are closed lakes that sit just short of spilling.
Their water balance is right for the evaporation they're given (inflow = evaporation off the lake, checked on
8 giant frames), but scaling lake_evap by 0.85 on the same frames turns 5 of 8 open, and an open lake drains
to its outlet valley (PW-055): seed 42 @144 Myr 6.85 -> 0.11 Mkm2 (all lakes 7.2 -> 0.4 Mkm2), seed 77 @480
4.62 -> 0.05, seed 3199 @52 5.16 -> 0.87, seed 1 @208 1.20 -> 0.09, seed 1 @288 3.34 -> 0.14 (hyperarid
basins, e.g. seed 1 @52 under 21 mm of rain, grow instead, as they should). So the giant closed lakes in
wet country (the ticket's "closed under 1000-1700 mm of rain") are largely a too-high open-water evaporation.
Inland drainage would fall with it (those basins drain), so check PW-054 alongside.

Simplest sound fix to try: drive open-water evaporation by the surface radiation the climate already has
(the Angstrom factor `0.25 + 0.5 x sunshine(cloud)` used for `par`), e.g. Priestley-Taylor on net
radiation, or at least Oudin on surface instead of top-of-atmosphere radiation for lakes; then check
`tools/earth_check.py` (Caspian, Aral, Chad, Eyre stay closed; Victoria, Great Lakes open) and the health
sweep's giant-lake frames. The zoom's lake balance uses the same `open_water` x pet (zoom.py ~1777).
- [ ] humid-tropics open-water evaporation ~1300-1600 mm on Earth's climate
- [ ] Earth's closed basins stay closed in earth_check

## Updates
- 2026-10-16: Merged inbox draft draft-zoom-lakes-penman.md ("The zoom's lakes still evaporate open_water x the land's PET, the world's lakes Penman's (PW-358)", found by pw015-rain).
  PW-358 (PW-015 branch) made the climate's `lake_evap` Penman's open-water evaporation
  (`climate.open_water_evap`, on the clouds and the air's humidity), which the run and world lakes use.
  `zoom.py` (~line 1906) still rebuilds a lake's loss as `TUNE["open_water"] x pet - evaporation` from the
  world's layers, so a zoom's lakes evaporate the old Oudin x 1.2 (humid tropics ~25% more, deserts ~35%
  less than the world's). Store the climate's `lake_evap` as a world layer (world.py) and use it in the zoom;
  then `TUNE["open_water"]` can go.
  - [ ] zoom lakes use the world's lake_evap; open_water removed
- 2026-10-16: Merged inbox draft draft-pw300-after-pw358.md ("PW-300 after PW-358's Penman lakes: giant-lake frames unchanged (13.6 -> 14.7% of L6 frames)", found by pw015-rain).
  For PW-300 (probably `--merge-into PW-300`). PW-358 (PW-015 branch, with stage 2's rain) replaced the lakes'
  Oudin x 1.2 by Penman's open water on the climate's cloud and humidity. On Earth L6 humid lakes evaporate
  less (Amazon floodplain 2007 -> 1487 mm, Lake Victoria 1663 -> 1217) and desert ones more (Nasser 1696 ->
  2629, Caspian 855 -> 1417); Earth's closed basins stay closed (earth_check). But on generated planets
  (health --quick, 8 L6 seeds x 500 Myr, frames after 50 Myr) the share of frames with a lake over 1 Mkm2 is
  unchanged within seed noise: 13.6% -> 14.7% (per seed 16 6 14 9 10 18 22 14 -> 29 14 21 9 20 5 12 6); lakes
  0.55 -> 0.48% of land, inland drainage 4.6 -> 6.7%. The same sweep's rain changed too (arid 29 -> 36% of
  land), so the giant lakes' basins got drier as their humid lakes' evaporation fell. Re-check which
  climates the giant lakes now sit in before trying more (basins-lakes write-up's replay scripts).
- 2026-10-16: Status todo -> in-progress. With PW-015.
- 2026-10-16: Coordinator: should use the same physics as PW-015's decision 1 (bulk/humidity-aware evaporation for open water); land with or before PW-015.
- 2026-10-16: Created from inbox draft draft-open-water-evaporation-clouds.md (found by basins-lakes).
