---
id: PW-583
title: "After PW-582's three attempts the Barents still freezes (-13.3 C): the inflow now reaches and sinks there (1.4 Sv) but arrives at -0.5 to +1.5 C, against ~4-6 C observed; Iceland -11.6 against the -7.8 bar"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: ocean
effort: l
impact: high
found_by: base-climate-laneA7, base-climate-laneA8, base-climate-laneA9
blocked_by: []
relates: [PW-582, PW-575, PW-458, PW-579]
refs: [planet/ocean.py, docs/review/base-climate/stages.md, docs/review/base-climate/laneA9/]
created: 2026-10-22
updated: 2026-10-23
---

## Description
PW-582 used all three attempts (stages.md, "PW-582, attempt 3 of 3"). Attempt 3 built both fixes the lane A8 draft
identified:
- **Straits by geometry** (`ocean._straits`): the inflow can't pass where the sea's narrowest cross-section, down to
  the layer's depth, is smaller than its own (`moc_width` x `moc_layer_m`). `moc_sill` is gone. The Barents opens
  (narrowest section 129-153 km2 against 125), while Bering (7), Hudson Strait (36), Nares (35) and Davis (120) stay shut.
- **The Arctic branch**: the inflow dives under the year-round ice where it meets it and can sink at the lid's edge
  with the winter water of the open sea it came through.

Earth L6 after: Barents / Kara sinking 0 -> 1.37 Sv, Nordic 4.0 -> 5.3, Baffin 2.4 -> 0.3, NH 10.2 -> 11.9 Sv at 91%
open polar sea. Fennoscandia -8.2 -> -6.5 (bar +-6), the Nordic Seas -5.5 -> -3.1, the Norwegian coast's sea air
1.4 -> 3.4 C (NCEP ~3.5). **But the Barents stays frozen (-13.7 -> -13.3), and Iceland is worse (-10.6 -> -11.6).**

Why, from the maps (`scratchpad/laneA9/nordic.py`, Earth L6):
- The inflow reaches the Barents (share 0.6-0.9) but its temperature falls from ~3 C off northern Norway (72N 6E)
  to 1.4 at the Barents' mouth and -0.4 at 38E. Observed: ~6-7 C off Norway, 4-6 C into the Barents. The Norwegian
  Atlantic Current is already ~3 C too cold at 70-72N.
- Each 220 km cell gives up heat as an exchange of ~0.4 Sv (`moc_lambda` 30 W/m2/C over `moc_width`). The transport
  along the path falls fast because the hemisphere's sinking, capped at `moc_k` x its density difference, is spread
  over every gated cell of the Nordic Seas by area. So little transport is left by 72N, and it cools within a few
  cells.
- The lid-edge sinking is small (~0.01-0.02 Sv per cell). The open water next to the lid is lighter than the
  deep-water reference by the time it gets there.
- Iceland: the Irminger branch west of Iceland arrives 3-4 C colder (t_in at 64N 30-40W 9 -> 4-5 C), because the
  sinking moved north and east (Nordic and Barents up, Baffin down).

Options:
- A: the sinking's distribution within a capped hemisphere. Today the cap scales every gated cell the same, so the
  transport is spread thin over the whole Nordic basin. Weighting by the water each cell actually receives (sinking
  where the inflow can feed it) would keep more transport along the boundary current. That is a mechanism question
  for the overturning's flow law, not a constant.
- B: the inflow's heat loss: `moc_lambda` exchanges with the latitude's sea temperature, not with the winter air
  over the inflow. Check its form against the observed heat loss of the Norwegian Atlantic Current (~5 C over
  ~1500 km at ~7 Sv).
- C: park the Barents until the winds' stage (its cold high), and accept Iceland's -11.6 as a cost of sounder
  routing.

- [ ] rule A / B / C (PW-582's three attempts are used)
- [ ] Iceland's regression (-10.6 -> -11.6): accept or chase with A

## Updates
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Coordinator 2026-10-22: parked (option C) after PW-582's three attempts; revisit after stage 3 and with the winds. Lean for later: option A (how sinking is spread within a capped hemisphere).
- 2026-10-22: Created from inbox draft draft-barents-still-frozen-after-pw582.md (found by base-climate-laneA7, base-climate-laneA8, base-climate-laneA9).
