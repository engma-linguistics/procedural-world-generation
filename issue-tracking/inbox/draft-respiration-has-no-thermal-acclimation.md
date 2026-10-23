---
title: "Plant respiration follows Q10 = 2 with no thermal acclimation, so a 2 C tropical cooling raises tree NPP ~15% and greens the tropics: the main channel of the time zoom's remaining low-latitude darkening at mild CO2"
type: task
status: todo
parent: PW-470
milestone: later
subsystem: timezoom
effort: m
impact: med
found_by: base-climate-laneA22
blocked_by: []
relates: [PW-644, PW-645]
refs: [planet/vegetation.py, docs/review/base-climate/laneA22/lowlat.py, docs/review/base-climate/laneA22/lowlat_split.py]
---

## Description
Lane A22 took the cooled climate's effect on Earth's plants apart (`laneA22/lowlat.py`, `lowlat_split.py`; L4,
dT -4 C, so the tropics cool ~2 C). Tree area at |lat| < 15 deg, against 13.8 Mkm2 at the start:
- the cooled climate, CO2 unchanged: 18.0 Mkm2;
- the cooled temperatures with the start's rain: 19.4;
- the cooled temperatures inside the plants, with the start's PET: 17.8;
- the cooled PET alone: 14.7;
- the cooled rain alone: 13.2.

So the tropics green under cooling mostly through the plants' own temperature response, not the water balance.
In `_year`, the growth curve is flat over 20-32 C for the tropical trees, which leaves maintenance respiration:
`(rl x LAI + rw) x 2^((t-20)/10)`. Trees, with their wood respiration rw, gain most when it is cooler.

Real respiration acclimates within weeks to months (Atkin & Tjoelker 2003; Smith & Dukes 2013). Over a forest's
life the NPP/GPP ratio stays near ~0.45-0.5 whatever the climate (Waring et al. 1998). An instant Q10 is right for
a day's weather, not for a 10 kyr glacial.

Since PW-644 (lane A22) the low CO2 of a real glacial outweighs this term: Earth's zoom at its glacial maximum
loses tropical forest. The forest test's milder CO2 term (-1 C at -4 C, a quarter share) still darkens below 40 deg.

What to try: acclimate respiration to the cell's own long-term climate. That means a reference temperature that
follows the growing season's mean, or respiration as a fixed share of GPP with Q10 only for the month-to-month
swing. This changes today's vegetation map too, so it needs re-tuning against `tools/veg_check.py` and Earth's
NPP. Not a v1 item unless the forest test needs it.
- [ ] Respiration acclimates to the site's climate. A uniform cooling of a few C changes tropical tree NPP by
  less than the cooling's direct Q10 would.
