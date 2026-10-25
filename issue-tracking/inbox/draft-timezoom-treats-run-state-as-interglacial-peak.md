---
title: "Time zoom treats the run's moment as the interglacial peak; the run's erosion, weathering and sea level never see the glacial half of an icehouse"
type: task
status: needs-decision
parent: null
milestone: null
subsystem: timezoom
effort: m
impact: med
found_by: coupling-audit
blocked_by: []
relates: [PW-470, PW-471]
refs: [planet/timezoom/cycle.py, planet/timezoom/forcing.py, planet/tectonics/earth.py, docs/overview.md, docs/review/coupling-audit/]
---

## Description
Coupling audit finding C4 (severity medium for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/timezoom/cycle.py Index (I starts 0 "interglacial: the run's own climate, so the run's ice") and forcing.py Forcing.update L88-94: dTg = -I x cool <= 0, CO2 x glacial_pco2^I <= 1.

**Other side:** planet/tectonics/earth.py global_temperature / ice_sheets: the run's dT, CO2 and ice are the Myr-scale state with ice averaged over the orbits; docs/overview.md section 2.8 says a time zoom "swings around" the run's balance.

**Why they disagree:** The run is the long-run mean of an icehouse era but behaves as its warm extreme: in the zoom the mean state is mean(I) x cool colder. The run's 2 Myr steps then erode, weather, glaciate and set sea level at interglacial conditions throughout cold eras (Earth's icehouse is glacial most of the time).

**Measured:** 8 L7 time zooms (f778ab 41a7a4 f06bbb ddc091 fd187b 606a1b fc82c2 6e96d2, 300 kyr each): mean I 0.44-0.57; mean dTg -1.3 to -6.2 C (min -2.3 to -9.6); mean sea-level change -5 to -205 m. The zooms' start matches their run keyframe exactly (T, pCO2, ice, sea level), so the handoff itself is consistent.

**What to try:** Options: (A) document the run as the interglacial state (fix overview 2.8) and accept; (B) run the run's weathering/erosion/sea level at the cycle mean (apply mean(I) x cool, measured or a fixed ~0.5, inside icehouse eras); (C) centre the index on the run (I in [-a, 1-a]). Belongs with the ice-age epic (PW-470); A is a v1 doc fix.
