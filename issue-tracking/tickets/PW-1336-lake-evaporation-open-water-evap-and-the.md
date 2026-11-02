---
id: PW-1336
title: Lake evaporation (open_water_evap) and the server's cell inspector feed sky cover where they need sunshine
type: task
status: done
parent: null
milestone: v2
subsystem: climate
effort: s
impact: low
found_by: lane125
blocked_by: []
relates: [PW-1327, PW-358, PW-808]
refs: ["planet/climate.py::open_water_evap", "planet/climate.py::months", "planet/climate.py::shade", planet/nest.py, planet/server.py, "https://www.fao.org/4/x0490e/x0490e07.htm", docs/review/base-climate/tropical-cloud/diagnosis.md, docs/review/base-climate/v1-finish-12/README.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
Same conflation as PW-1327's summer split, found in three more readers. climate.compute passes the sky cover
(cloud_jul/jan) to open_water_evap (climate.py ~2700), nest.py (~170) passes out["cloud_jul"], and server.py (~330)
passes cloud/100 into climate.months for a cell's monthly chart. The Angstrom-Prescott relation used by
months/open_water_evap is in relative sunshine duration (FAO-56 ch.3), and months' docstring asks for the light's cloud
(shade). In the wet tropics the sky cover maps to less sunshine than the climate's own (afternoon showers), so lake net
radiation there is low and the inspector's chart differs from what the plants saw. Not measured: how much lake_evap moves.
Try: pass shade_jul/jan (climate.shade_from_hours of the sunshine layers) and compare Lake Victoria / Amazon
floodplain (PW-358: 1415 / 1406 mm) and the earth_check closed basins.
- [ ] lake_evap on shade; Earth's closed basins stay closed; inspector chart equals the plants' months

## Updates
- 2026-11-02: Status todo -> done. Lane 126 (merged fdc631a4): see docs/review/base-climate/tropical-cloud/round1.md. Earth warm-land shade 0.31/0.42/0.54 vs CRU 0.27/0.41/0.53; land >=35 C 7.9% -> 0.9% (NCEP 1.7%); Lake Victoria evap 1357 -> 1635 mm. L6 judge 32/36 vs 32/36, no hard failures, dT/CO2 unmoved; arid -2.0 pts, trees +5.7.
- 2026-11-02: Created from inbox draft draft-open-water-and-inspector-read-sky-cover.md (found by lane125).
