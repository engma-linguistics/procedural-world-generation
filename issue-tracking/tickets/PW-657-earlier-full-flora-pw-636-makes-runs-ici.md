---
id: PW-657
title: "Earlier full flora (PW-636) makes runs icier: icehouse share 29 -> 43%, ice sea level after 250 Myr -31 -> -50 m on the quick sweep"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: med
found_by: pw636-flora-pace
blocked_by: []
relates: [PW-636, PW-611, PW-576, PW-644, PW-434]
refs: [planet/vegetation.py, planet/tectonics/earth.py, docs/review/base-climate/thermostat.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-636 compresses the plant groups' timeline (`vegetation.FLORA_PACE` = 0.8), so flowering trees, grasses and
C4/succulents appear ~0.2 of the run earlier. `tools/health.py --quick` (8 L6 seeds, 500 Myr, same session,
8 workers; main 9b30887 against the branch) moves the ice one way:
- icehouse share, mean of the 8 seeds: 28.7% -> 42.7% (per seed main/new: 1 16/39, 2 20/29, 11 43/77,
  21 0/35, 3199 0/2, 42 63/55, 77 84/49, 505 4/55);
- keyframes with ice sea level below -150 m: 4.2% -> 11.5%; the deepest ice sea level -18..-322 m -> -37..-543 m
  (seed 505 -543 m);
- the mean ice sea level after 250 Myr is -31 -> -50 m, deeper on 6 of 8 seeds;
- the old ice bar fails on 0 -> 2 seeds (11, 505). The new bar (ice-v2-criteria) fails on 4 -> 2 seeds: 21, 77 and
  505 now pass, and 11 now fails at 77% icehouse;
- land NPP (380-500 Myr) is 320 -> 356 g C/m2/yr; the global temperature is ~0.15 C cooler on average; the CO2 index
  medians barely move.

The likely path: the full flora gives more NPP, so more weathering (earth.py's NPP factor) draws down CO2 and the run
cools. Main's runs reach the same state, but only in their last ~15%, so a larger share of each run is now in it.
That is the CO2 thermostat's question (PW-611; PW-576's CO2 stock and fixed start reference). How much should a
change in the sink, here a biological one, move the steady climate? PW-644 found the same direction through a
different path: the time zoom's plants darken the low latitudes under cooling. It is a direction, not a proof: the
runs are chaotic, and the ice fixtures on main are single-seed (PW-643).

Options:
- A: accept it. A planet with flowering plants for longer is icier, which is physical. Re-measure the icehouse share on
  PW-643's multi-seed harness and leave PW-611's band where it is.
- B: treat it as part of PW-611. If the thermostat lets the sink's biology shift the steady dT this much, fix that in
  the thermostat rather than in the flora's timing.
- C: soften the NPP factor's effect on weathering. Not recommended: it's a nudge on a downstream kernel to undo a
  correct upstream change (global, not local, optima).
- [ ] owner/thermostat lane picks; re-measure on the multi-seed harness

## Updates
- 2026-10-23: Created from inbox draft draft-earlier-flora-deepens-ice.md (found by pw636-flora-pace).
