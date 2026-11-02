---
id: PW-1354
title: Warm semi-arid lowland winters 1.6 C cold where the rain is right; the model warms dry sunny summers but not dry sunny winters
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane131
blocked_by: []
relates: [PW-1335, PW-1327]
refs: ["planet/climate.py::_summer_split", "planet/climate.py::_winter_air", "planet/climate.py::_air_temps", docs/review/base-climate/tropical-cloud/round2-diagnosis.md, docs/review/base-climate/tropical-cloud/winter2.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: after taking out height, warm semi-arid land on low ground (< 300 m, warm land at 250-900 mm where the
model's rain is within 30% of GPCC) still has its coldest month 1.6 C below NCEP. Its warmest month is 0.9 C above.
So the model's seasonal swing there is ~2.6 C too big. At 20-30 deg it is 17.1 C vs 13.9 observed. At 10-20 deg it is
right. The model's coldest month there is the land's own winter (`_winter_air`: temp0 less the continental swing), set
by latitude alone. `_summer_split` gives dry, sunny summers their extra sensible heat, but nothing does that for dry,
sunny winters. Lane 131's reading of the code, not sourced.

Try first (cheap diagnosis, no code): the winter half's sunshine, AET and PET on these cells and on the 40-60 deg
lowlands. Then what a winter twin of `_summer_split` would add with its own reference (the curve's winter, not the
summer's sun_ref), and whether it stays near 0 in midlatitude winters (low sun, stable air). Needs a source on the
dry-season surface energy budget of savannas before any code.
- [ ] diagnosis written; Earth warm semi-arid lowland coldest month within ~1 C of NCEP without moving 40-60 deg

## Updates
- 2026-11-02: Created from inbox draft draft-winter-energy-split-dry-season-warmth.md (found by lane131).
