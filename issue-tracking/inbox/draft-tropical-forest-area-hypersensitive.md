---
title: "The tropical forest's area moves 3-4% per 1% of tree productivity: a 20% CO2 drop alone takes Earth's |lat|<15 forest from 15 to 9 Mkm2, and a 2 C cooling grows it by a third"
type: task
status: todo
parent: PW-470
milestone: later
subsystem: timezoom
effort: m
impact: med
found_by: base-climate-laneA22
blocked_by: []
relates: [PW-644]
refs: [planet/vegetation.py, docs/review/base-climate/laneA22/lowlat.py]
---

## Description
In lane A22's runs of `laneA22/lowlat.py` on Earth L4 (the full model grown from scratch), the forest biome's area
at |lat| < 15 deg is 15.0 Mkm2 at the start. It moves to:
- 9.0 Mkm2 at CO2 index -1/3 alone. That is ~280 ppm under the plants' log2 reading. C3 light-use efficiency
  falls ~12% at 27 C (Farquhar's light-limited quantum yield; the response matches FACE, beta ~0.55).
- 20.3 Mkm2 at the climate 4 C colder alone (2 C in the tropics). Respiration's Q10 makes tree NPP ~15% higher;
  see `draft-respiration-has-no-thermal-acclimation.md`.

The water-use part of the CO2 response hardly matters there (wet tropics). So the forest-savanna split behaves like
a knife edge: the competition against C4 grass, with fire, turns a few % of NPP into tens of % of area. Some
bistability is real (Staver et al. 2011; Hirota et al. 2011). But Earth's model at preindustrial CO2 would have ~40%
less tropical forest than at the model's 350 ppm "today", which is too much. Earth's tropical forest did not grow
by half between 1850 and 1990.

What to look at: the fire-grass feedback's strength in `equilibrium` (C4 grass fuel, tree resist), and whether
the savanna trees (TrBR) or the forest trees win too sharply against grass at the margin. Measure the forest area's
response to a +-10% tree NPP change; ~1-2% of area per % of NPP would be closer.
- [ ] |lat| < 15 deg forest area changes by under ~20% between CO2 index 0 and -1/3 at today's climate
