---
title: "The time zoom's co2_share (0.5) gives CO2 twice its share of a glacial's cooling; Earth's glacial pCO2 lands plausibly (171 ppm) only because the interglacial reference is 350 ppm, not 280"
type: task
status: todo
parent: PW-649
milestone: later
subsystem: timezoom
effort: s
impact: low
found_by: base-climate-laneA23
blocked_by: []
relates: [PW-646, PW-644, PW-648]
refs: [planet/timezoom/params.py, planet/timezoom/plants.py, planet/climate.py, docs/review/base-climate/laneA23/co2_choices.txt]
---

## Description
Since PW-646 (lane A23) the plants read a real pCO2: the run's (`climate.pco2`, 350 ppm x e^co2) and, in the
time zoom, `co2_c / co2_sensitivity` doublings away from it, where `co2_c = co2_share x` the glacial cooling.

Earth's zoom at its glacial maximum (cooling 6.22 C at L6): `co2_c` = -3.11 C, -1.04 doublings at 3 C per
doubling, so 171 ppm. That is plausible against the LGM's ~185-190 ppm (ice cores), and the bars and forest bands
in `laneA23/tz_earth_c.txt` match lane A22's.

The ratio is off, though:
- glacial / interglacial is 0.49 in the zoom against Earth's 0.68 (190 / 280);
- CO2's own share of the LGM's ~6 C, at 3 C per doubling, is 3 log2(190/280) = -1.7 C, about 27%, not half.
  `co2_share`'s "Earth's LGM ~half" counts the feedbacks CO2 sets off (ice albedo, dust, other gases); the
  plants feel only the CO2.

Two errors cancel for Earth:
- `co2_share` overstates CO2;
- the interglacial starts from the climate model's "today" (350 ppm, the late 20th century the climate data show),
  where Earth's interglacials stood at ~280.

What to try, if the low-CO2 plants ever need it (they matter a lot: PW-648, a 350 -> 171 ppm drop alone takes
Earth's forest biome from 56 to 35 Mkm2 at today's climate, `laneA23/lowtail_L6.txt`):
- `co2_share` ~0.3 (CO2's own forcing share);
- the climate model's dT = 0 read as ~280 ppm plus the ~0.5 C of industrial warming in its data.

Earth would then land near 280 x 2^(-0.62) ~ 180 ppm, with the right ratio. Both changes move today's plants (the
CA_REF the C3 efficiencies were tuned at) and every run's plants, so it is a calibration pass, not a v1 item.
- [ ] The zoom's glacial/interglacial pCO2 ratio is within ~0.6-0.75 on Earth, with its glacial pCO2 still 170-210 ppm
