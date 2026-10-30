---
id: PW-1050
title: The run's ice and its climate catch up one step per climate update, so how much ice a run grows depends on how often the climate is updated
type: task
status: needs-decision
parent: PW-247
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: lane27b
blocked_by: []
relates: [PW-247, PW-470, PW-364]
refs: [planet/tectonics/earth.py, docs/review/speed/README.md, docs/review/speed/iceprobe.py]
created: 2026-10-29
updated: 2026-10-30
---

## Description
**In plain words.** A run updates its weather every few million years. After each weather update the ice sheets
grow or shrink to fit that weather. But the weather does not "see" the new ice (its white surface, its own cold
air) until the next update. So the ice and the weather catch up with each other one step per update. Update more
often, and the ice catches up faster and grows further before the slow drivers (CO2, the drifting continents)
change again. Updating every 2 Myr instead of every 4 Myr gave ice-age-heavy planets ("iceboxes") in 10 of 18
test worlds instead of 2. This means the amount of ice in a run is partly set by a computing choice, not by the
planet. Iceboxes are reported as colour, not failures (they don't fail a world), so nothing is broken for v1.
But it is a soundness gap: the update rate should not decide how icy a planet is.

**Evidence** (L6 paired judge, 18 draws, roll 0.0005, 300-990 Myr; lane 27/27b, docs/review/speed/README.md):

| arm | climate cadence | iceboxes | share of steps with ice sea level < -150 m | ice sea-level path, m/Myr | m per update that moved | albedo term | finish-moment T |
|---|---|---|---|---|---|---|---|
| main | 4 Myr | 2 | 0.07 | 1.14 | 2.5 | +0.12 C | +2.8 C |
| C (default) | 8/4 Myr + 1 C dT trigger | 3 | 0.00 | 0.79 | 3.4 | +0.17 C | -0.6 C |
| E | 2 Myr (every step) | 10 | 0.17 | 1.84 | 2.2 | -0.28 C | -0.8 C |

The ice moves by a similar amount per update in all three arms (2-3 m of sea level), so its speed per Myr scales
with the update rate. `earth.ice_sheets` solves the sheets to their fixed point under each update's climate, but
`climate.compute` sees the previous update's ice (`earth.update_climate`). PW-364 removed the same kind of
per-update limit inside the ice passes; the outer ice-climate loop still has it.

## Candidates (diagnosis only; not run)
1. **Iterate the ice-climate loop inside an update** while the ice moved by more than a threshold (say 5 m of sea
   level): climate.compute again with the new ice. ice_sheets' docstring measured "+80% of the climate at L5" for
   always re-solving. Only re-solving when the ice moved a lot should cost much less, because most updates move
   it by about 2 m.
2. **A cheap inner loop on the ice's own feedbacks only**: after ice_sheets, re-apply the sheet's surface cooling
   (climate.ice_surface) and the albedo term, then re-run the ice passes, without a new climate.compute. Cheaper,
   but it leaves out the rain's response to the ice.
3. **Accept it and fold it into PW-470** (ice ages done properly, post-v1). This keeps C's cadence, whose ice
   is close to main's.

Decision needed: is this a v1 soundness gap (the owner's bar is "flag visible unsoundness"), or does it go
under PW-470? Whichever fix is chosen, its success test is that arms at 2 and 4 Myr give the same icebox count
on the paired judge.

## Updates
- 2026-10-30: Lane 28 diagnosis (probes only, scratchpad lane28; write-up docs/review/base-climate/ice-loop/README.md). Repeating the update on the same ground and dT at 16 moments: the loop usually converges within 1-2 updates; the '2-3 m per update' is mostly +-0.5-1 m margin flicker, so the per-Myr ice path rises with the cadence trivially. The real gap is at onsets: seed 53669 at 700 Myr walks -74 -> -97 m over 6 updates and is still growing; holding the sheets' carried air (PW-336) makes the walk vanish. Frozen drivers: 2/4/8 Myr cadences end within a few m, but an onset takes ~3x longer at 8 Myr, and under a 10 Myr cold dip 2 Myr ends on the iced branch (-84 m) and 8 Myr not (-68 m). Fix chosen (coordinator 10-30): candidate 2, the carried air's rounds within the update (climate.compute's reground, earth.ice_air_rounds, Params.ice_air_rounds 4): the onset state reaches -102 m in one update. Dropped: ice re-settled between updates on temp_response-shifted ground (overshoots: -58 m vs the 2 Myr arm's -33). Candidate 1 (full re-solve) costed at +30-45% of a run.
- 2026-10-29: Created from inbox draft draft-ice-climate-loop-steps-per-update.md (found by lane27b).
