---
title: With the margin flicker cured, the sea-floor creep still cools the world by about 3 C
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-115
blocked_by: []
relates: [PW-1295, PW-1292, PW-950]
refs: [planet/surface.py::_creep, planet/tectonics/crust.py::coherence, planet/tectonics/crust.py::necking, docs/review/tectonics/margin/pw1295-note.md, docs/review/tectonics/margin/deep-dive.md, docs/review/tectonics/margin/note-arc-co2.md, docs/review/tectonics/margin/diagnosis-land.md, docs/review/tectonics/margin/tracediag.py]
---

## Description
In plain words: PW-1295 stopped the continents' outer cells from flipping between continent and ocean floor (the
shred bound is now 15 km, below the 20 km birth bound). With the sea-floor creep on, that brings the continental
churn down to main's level (born 19 000 / 16 800 km x cells per 400 Myr against 43 000; coherence -5 500 / -7 100
against -40 000). But the creep still runs colder: on seeds 1 and 3 (L6, 600-1000 Myr), creep + the 15 km bound has
late dT -3.3 / -4.4 C against -0.3 / -1.7 without the creep, pCO2 616 / 471 against 933 / 763, and land
32.4 / 31.2% against 34.0 / 33.1%. So the churn was not what cools the creep's worlds (deep-dive.md judge 2: -2.6 C,
2 frozen over).

What to try:
- [ ] trace the source and sink (tracediag.py `src`, `sink`, `ridge`, `arc`, `supply`) for creep vs no creep on top
  of the 15 km bound: which side of the CO2 balance moves (note-arc-co2.md, diagnosis-land.md had the volume
  thermostat and the drowned margins as candidates)
- [ ] only then a paired judge of the creep (`neck_km=200 rise=1 slope_k=1000`) against main

Screens: pw1295-note.md section 2, scratch runs deleted; redo with tracediag.py and `--set star_brightening=1.0
neck_km=200 rise=1 slope_k=1000`, seeds 1 and 3, 1 Gyr, L6.
