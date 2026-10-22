---
id: PW-454
title: A colder climate greens the model's dry tropics, so glacial vegetation darkens them (Earth's LGM dried and browned them)
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: med
found_by: pw450
blocked_by: []
relates: [PW-450, PW-448, PW-435]
refs: [planet/vegetation.py, planet/climate.py, planet/timezoom/plants.py, docs/review/audit/PW-450-vegetation.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-450 gave the time zoom the run's vegetation. Its glacial feedback is about a quarter of Earth's LGM
value (Köhler et al. 2010: -1.1 W/m2), and half of the gap is a sign error in the tropics. Earth L6, today's
surface, prescribed global cooling, plants grown from the start's balance (`scratchpad/pw450/probe.py`):

| global cooling | F, all (W/m2) | 45-90 N | 30-45 N | 30 S-30 N | tree cover, 45-90 N | tropical trees |
|---|---|---|---|---|---|---|
| -2 C | -0.09 | -0.15 | +0.03 | +0.03 | -4.5 Mkm2 | +1.3 Mkm2 |
| -4 C | -0.17 | -0.35 | +0.05 | +0.12 | -8.7 | +2.7 |
| -6 C | -0.32 | -0.58 | +0.05 | +0.20 | -12.1 (of 21) | +3.9 |

The boreal half behaves about as it should: forest becomes snow-covered tundra, at ~0.05 W/m2 per Mkm2.
But the tropics and the 30-45 N belt *gain* trees as the planet cools. Most of the gain is in cells
with sparse trees today (savanna and dry woodland; the Americas have 1.45 of the 1.9 Mkm2 at -6 C).
Two reasons: (1) the climate's potential evaporation falls with temperature faster than its rain does
(rain scales by q_k = 0.06 per C), so a colder planet is a wetter one for its plants; (2) the
vegetation's CO2 effect is mild (C3 efficiency x (1 + 0.12 x index), plus a C4 shift), so glacial
CO2 starvation doesn't push trees back toward grass.
Earth's LGM was drier in most of the tropics and subtropics. Rainforest and woodland shrank and
grassland and desert spread (Prentice et al. 2011, Bragg et al. 2013), and about half of that comes
from low CO2 alone (Harrison & Prentice 2003). That brightening is a good part of the -1.1 W/m2.
Try: check the glacial hydrology first. Does the model's rain over tropical land fall at all relative
to its potential evaporation when it cools? (PW-448 found that its Canadian interior lacks the summer
cooling, too.) Then check the plants' CO2 response against LPJ-type sensitivities. Both are the run's
models, so the cold eras need re-measuring as well.
- [ ] at a prescribed -6 C, tropical tree cover falls (or at least doesn't rise), and the vegetation
  term reaches ~-0.6..-1.1 W/m2

## Updates
- 2026-10-20: Created from inbox draft draft-glacial-tropics-green-not-dry.md (found by pw450).
