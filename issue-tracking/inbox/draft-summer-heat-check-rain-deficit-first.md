---
title: "PW-1279 diagnosis: check how much of the hot low-latitude summers is the dry-coast rain deficit (observed-rain swap)"
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: lane120
blocked_by: []
relates: [PW-1279, PW-015]
refs: [docs/review/base-climate/rain-inland/diagnosis.md, tools/earth_check.py, planet/climate.py::_summer_split, planet/climate.py::_land_finish, planet/climate.py::compute]
---

## Description
In plain words: the places where the model is too dry are also the places where its summers run too hot, because
wet ground cools itself by evaporating. Before PW-1279 changes heat capacity or clouds, it should check how much of
the extra heat goes away when the model gets the right rain.

Earth L7 (main 3b5c9935), warmest month model / NCEP, with rain model / GPCC:
- SE USA 30.4 / 25.3 C, rain 719 / 1329
- Pampas 31.5 / 25.1, rain 394 / 943
- India 33.3 / 32.6, rain 627 / 1126 (BWh against Aw)
- E Australia 28.6 / 23.7, rain 551 / 737
- Kolkata 38.0 / 31.1, rain 193 / 1725

Lane 120's land friction screen (fric_land 0.72) wets SE USA to 960 mm, and its warmest month cools to 29.2 C. That
is ~0.5 C per 100 mm, through `_summer_split`.

To do, for PW-1279's diagnosis gate:
- run Earth's summer energy split with GPCC rain swapped in for the model's;
- report the warmest month by latitude band, with and without the swap.
- [ ] the share of the low-latitude warm-month excess that the rain swap removes, in PW-1279's write-up
