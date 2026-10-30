---
title: The rain kernel's own water cycle runs ~1.56x too fast (vapour lasts 4.1 days over land, 6.1 over sea, against ~9 observed); the global rescale hides it
type: task
status: todo
parent: PW-015
milestone: v2
subsystem: climate
effort: m
impact: low
found_by: lane58
blocked_by: []
relates: [PW-1093]
refs: [planet/climate.py, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
---

## Description
In plain words. The model's rain machinery rains its vapour out about 1.6 times faster than the real atmosphere. Over
land it does so 1.5 times faster still than over the sea, where in reality the two are about the same. The model then
scales all its rain down to Earth's 1000 mm/yr, which hides the speed but not its effects: vapour doesn't travel far
enough, and land keeps its own vapour (75% of land evaporation rains back on land; the reference value is ~57%).

Earth L6/L7, 347b4374 (`tools/moisture_regions.py`):
- The kernel's global rain in physical units (the open-sea fit of 9.8 mm of column per vapour unit): 1560 mm/yr;
  compute rescales it x0.64.
- Vapour residence (PW / P):

  | | model, Apr-Sep / Oct-Mar | observed (NCEP PW / GPCC, GPCP P) |
  |---|---|---|
  | land | 4.1 / 4.2 d | 9.9 / 8.7 d |
  | sea | 6.1 / 6.0 d | 9.2 / 8.8 d |

- Slowing every rate x0.64 (kernel probe) makes the land *wetter* (1047 -> 1128 mm): more sea vapour reaches the
  continents. So it isn't PW-1093's fix.
- The land-sea gap in residence is the part that matters. The cubic humidity gate makes it self-restoring: halving the
  land's rates poleward of 35 deg moves the land's residence only 4.1 -> 4.4 d (L7).

To decide: whether the rates should carry physical units (no rescale), and what holds the land's residence near the
sea's. Low priority. It's a consistency check, and Earth's rain pattern doesn't need it now.
