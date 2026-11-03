---
title: "The run never sees the planet's eccentricity: a fixed 0.03 in the ice cycle, no annual-mean gain; any per-planet eccentricity must reach the run too"
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane148
blocked_by: []
relates: [PW-1365, PW-481, PW-555, PW-443]
refs: ["planet/icemass.py::cycle_dq", "planet/icemass.py::ECC", "planet/timezoom/params.py::TZParams", "planet/tectonics/earth.py::star_forcing", "planet/make.py::UNSUPPORTED", docs/review/climate/eccentricity/round1.md, docs/review/climate/eccentricity/runs_summary.py, tools/hard_bar.py]
---

## Description
In plain words: the planet's orbit is set in two unconnected places. The ice-age time zoom draws Earth's cycle
(e 0.002-0.052, `ecc_mean 0.027`). The 1 Gyr run, which decides whether a world freezes, boils or loses its CO2,
uses a fixed e = 0.03 for its ice and leaves out the extra yearly sunlight of an eccentric orbit
((1 - e^2)^-1/2: +0.5% at 0.1, +2.1% at 0.2). Today that is harmless, because both are Earth-like. But if the
generator ever draws e per planet (PW-1365's decision), the run must take the same draw.

The run is also very sensitive to it. Lane 148's screen (PW-1365 round 1; a scratch copy with `icemass.ECC` set
from an env var and the yearly gain as `climate_offset`; 4 L6 seeds, 1 Gyr) found:
- At e = 0.1, the run's land ice vanished on all 4 seeds (median iced land after 300 Myr 0%, icehouse time 0-1%,
  against 1.4-8.1% and 21-68% for the same seeds on today's code). The run's ice rule turns insolation into
  temperature at `INSOL_K` 0.25 C per W/m2, ~3x the land's seasonal response (PW-459). So a +100 W/m2
  perihelion summer means +25 C of melt in the cycle mean. Real Earth at 0.06 has ice ages, so this is the rule's
  overshoot, not physics. (See round1.md for the ablation without the yearly gain.)
- Soft passes fell 3/4 -> 1/4 (0.1) -> 0/4 (0.2) on the finish's temperature check (ends +4 to +8 C without the
  ice's albedo). No hard bar fired at 0.1-0.2.

To do when per-planet orbits come in (with PW-481's orbit parameter):
- [ ] one orbit draw per planet feeds the run's ice cycle (ECC), the run's yearly sunlight (as star forcing, so the
  thermostat answers it) and the time zoom's ecc_mean
- [ ] the run's ice rule uses the seasons' response (PW-555 stage 3) before e above ~0.06 is allowed, or the
  run's ice ages disappear
