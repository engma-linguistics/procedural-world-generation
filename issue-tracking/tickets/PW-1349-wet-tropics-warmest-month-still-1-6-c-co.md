---
id: PW-1349
title: "Wet tropics' warmest month still ~1.6 C cool on Earth after the split reads sunshine: the model's rain there is 2-3x"
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: m
impact: low
found_by: lane126
blocked_by: []
relates: [PW-1327, PW-228, PW-1335, PW-1330]
refs: ["planet/climate.py::_summer_split", "planet/climate.py::water_balance", docs/review/base-climate/tropical-cloud/round1.md, docs/review/base-climate/tropical-cloud/diagnosis.md, docs/review/base-climate/summer-heat/diagnosis.md, docs/review/base-climate/tropical-cloud/screen.py, data/earth/L7.npz]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: lane 126 made the summer heating read the sunshine and thinned the tropics' cloud. Even so, Earth's
0-20 deg warmest month is 24.8 C against NCEP 26.5 (main 24.6). The Sahel is -3.9 C and the W Africa coast -2.8.

Summer sunshine there is now 0.40 / 0.48 (0-10 / 10-20 deg) against CRU 0.46 / 0.57, so sunshine is no longer the
main gap. What's left is evaporation from too much rain. Lane 121's table has the Sahel at 2094 mm (GPCC 596) and
W Africa at 2539 mm (GPCC 1455), and its LE swap took +2.1 C off the Sahel bias. So this is PW-228's regional rain,
not the split.

Try: nothing in the split. Re-measure the 0-20 deg warm month after the rain round.
- [ ] 0-20 deg warmest month within ~1 C of NCEP once the Sahel / W Africa rain is right

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-11-02: Created from inbox draft draft-wet-tropics-summer-cool-from-rain.md (found by lane126).
