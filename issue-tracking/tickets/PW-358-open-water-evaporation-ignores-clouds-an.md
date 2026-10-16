---
id: PW-358
title: Open-water evaporation ignores clouds and humidity, so wet basins stay closed and hold giant lakes
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: med
found_by: basins-lakes
blocked_by: []
relates: [PW-300, PW-054]
refs: [planet/climate.py, planet/hydrology.py, docs/review/audit/basins-lakes.md]
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
- 2026-10-16: Coordinator: should use the same physics as PW-015's decision 1 (bulk/humidity-aware evaporation for open water); land with or before PW-015.
- 2026-10-16: Created from inbox draft draft-open-water-evaporation-clouds.md (found by basins-lakes).
