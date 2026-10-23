---
id: PW-644
title: The time zoom's plants grow trees and grass below 40 deg under glacial cooling (+0.13 W/m2 of darkening on every world, Earth included), where Earth's glacials shrank the tropical forests
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: timezoom
effort: m
impact: med
found_by: base-climate-laneA21
blocked_by: []
relates: [PW-450, PW-640]
refs: [planet/timezoom/plants.py, planet/vegetation.py, docs/review/base-climate/laneA21/fpool.txt, docs/review/base-climate/laneA21/fearth_L6.txt]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A21 took the forest-to-tundra test's forcing F apart (`laneA21/fdiag.py`; the climate 4 C colder, CO2 term
-1). On every world, the snow-free land below 40 deg darkens:
- F there is +0.13 W/m2 on average over 240 L4 worlds;
- tree area there grows by +1.7 to +2.6 Mkm2;
- grass and bare-ground changes give another +0.06.

Earth does the same: +0.10 at L4 and +0.12 at L6, with +2.3 Mkm2 of trees below 40 deg at L6.

Earth's glacials went the other way. At the LGM the tropical and subtropical forests shrank and grassland and
desert spread. Drier air, a weaker water cycle and low CO2 drove it (pollen syntheses, e.g. BIOME 6000; Prentice
et al. 2000), and this is part of the LGM's ~-1.1 W/m2 vegetation forcing (Köhler et al. 2010). The model's
cooling probably lowers the evaporative demand more than the rain, so the subtropics get wetter for the plants. The
CO2 index's effect on the plants' water use may also be too weak. Worth checking:
- the rain's change against the PET's in the 0-40 deg belt under dT -4;
- the plants' CO2 response at co2_c -1.

This term is also why the forest test fails on warm worlds (`draft-forest-test-premise-is-planet-dependent.md`).
It is not a fixture issue: if the low latitudes dried as on Earth, the premise would hold on more worlds. Earth's
F (-0.24 W/m2 at L6) is also a fifth of Köhler's, though the test's 10 kyr at -4 C is not an LGM.
- [ ] The 0-40 deg vegetation response to glacial cooling is plausible against the LGM (direction first)

## Updates
- 2026-10-23: Created from inbox draft draft-cooling-greens-the-low-latitudes.md (found by base-climate-laneA21).
