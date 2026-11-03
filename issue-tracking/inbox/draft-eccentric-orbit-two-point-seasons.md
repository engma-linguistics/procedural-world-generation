---
title: "An eccentric orbit's near-sun season is read only through July and January: above e ~0.1 a world's seasons depend on where perihelion falls in the calendar"
type: task
status: todo
parent: null
milestone: v3
subsystem: climate
effort: m
impact: low
found_by: lane148
blocked_by: []
relates: [PW-1365, PW-1325, PW-397, PW-443]
refs: ["planet/climate.py::_orbit", "planet/finish.py::orbit_dt", "planet/timezoom/forcing.py::orbit_anomaly", "planet/orbit.py::insolation", docs/review/climate/eccentricity/round1.md, docs/review/climate/eccentricity/measure.py]
---

## Description
In plain words: the climate keeps only a warm and a cold half-year. When a finished world adds its orbit
(PW-1325), it reads the orbit's monthly anomaly in just two months, July and January. That is fine for
Earth-like orbits (e < ~0.06). On a strongly eccentric orbit, the near-sun passage is short (Kepler) and can fall
in any month, so the model misses it. It gets the hot season wrong, and can even make the world colder.

Measured (lane 148, PW-1365 round 1, seed 957317 at L6, 100 kyr time zoom at a fixed e, finished world):
- With perihelion at the March equinox, against the same seed at e = 0: at e = 0.3 the open land's mean warmest
  month falls from 22.3 to 15.9 C and land with no thaw month rises from 0.1 to 8.5%. Yet the annual sunlight is
  4.8% higher. Meanwhile the time zoom's ice, which sees all 12 months, melts from 9.6 to 0.7% of the land.
- With perihelion on the northern solstice, land >= 35 C peaks at e = 0.3 (23.5%) and falls back at 0.4
  (15.8%). At 0.4 the largest monthly anomaly is 686 W/m2, but July gets 161 W/m2 at 20 N.

Only matters if the generator ever draws e above ~0.1 (PW-1365's decision; post-v1 weird worlds, PW-443). A fix
would use each cell's anomaly in its own warmest and coldest month (max/min over the 12 months, with the half-year
rain kept on the matching half), not July and January. Then check that Earth-range orbits are unchanged
(goldens, earth_check).
- [ ] the warm/cold season takes the anomaly's own extreme months; e <= 0.06 worlds unchanged within noise
- [ ] an equinox-perihelion e = 0.3 world is not colder than its circular twin in its warmest month
