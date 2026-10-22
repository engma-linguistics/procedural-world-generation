---
title: "PW-582 attempt 1: the Barents stays frozen (-13.7 C) because it never sinks, so no inflow is routed to it; Iceland -10.3 against the -7.8 bar"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: ocean
effort: l
impact: high
found_by: base-climate-laneA7, base-climate-laneA8
blocked_by: []
relates: [PW-582, PW-575, PW-458]
refs: [planet/ocean.py, docs/review/base-climate/stages.md, docs/review/base-climate/laneA7/]
---

## Description
Lane A7's PW-582 attempt 1 (stages.md, "PW-582") makes the inflow follow the polar seas' slope and lets the lid be the
ice the overturning itself leaves. The Nordic Seas' coldest month goes -8.3 -> -4.2 C bias, Fennoscandia -8.9 -> -7.9,
Iceland -12.4 -> -10.3, the Norwegian coast's sea air -0.7 -> +2.0 C (NCEP ~+3.5). **The Barents doesn't move
(-13.7).**

Why, measured on Earth L6 (`scratchpad/laneA7/nordic.py` maps):
- The inflow is routed only to cells that sink (`ocean._route` from the sinking). The Barents' winter water is
  ~0.5 kg/m3 lighter than the Nordic Seas' (salinity 34.8 against 35.6-36.1), so it is gated out at every spin-up
  width tried (`moc_drho` 0.6, `moc_iters` 12). It is light because it isn't fed: a lock.
- On Earth the Barents is salty (~35.0) because the Atlantic water goes there anyway, and its cooled water is among
  the Arctic's densest.
- The model's Nordic inflow is also too salty (35.6-36.1 against ~35.2): `_along` relaxes the inflow's temperature
  toward the latitude's but never its salinity (no lateral mixing), which widens the Barents' density gap.

Tried and dropped:
- **Knudsen's exchange** for the sea under the lid (Q_in = F S_out / (S_in - S_out), routed to the lid's edge). It gives
  0.8 Sv on Earth (the lid's net fresh water is 0.05 Sv; the real Arctic takes in ~3 Sv). It warms the Fram side by
  ~1 C but enters the Barents only at its mouth. With a meltwater pulse it scales up unbounded (the real exchange is
  limited by the straits' hydraulics), and it broke `test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast`
  (57 m against 46). Its code is in `scratchpad/laneA7/exp_pw582.diff`.
- A thermal-wind (baroclinic) steering of the inflow: ~0.03 m/s, no effect.

Options:
- A: the inflow's salinity mixes with the water it passes (as its temperature does), so the Nordic water is
  realistic and the Barents' gap shrinks (it may then sink and feed itself). This weakens the overturning everywhere,
  so it needs the stage-1 bars re-checked.
- B: water-mass transformation along the path: a site sinks no more than its winter heat loss can turn the inflow
  into deep water (Walin 1982), and the rest goes on downstream. Its numbers on Earth are at the edge of binding.
- C: accept the Barents as frozen until the winds' stage (its cold high keeps the winds offshore).

Ruled (coordinator): A, then B if still short.

## Attempt 2 (lane A8): A landed, B measured, the lock is elsewhere
- **A** (the inflow's salinity relaxes toward the water it passes at its temperature's rate): the Nordic inflow is
  now 35.0-35.5 psu (was 35.6-36.1). The Nordic site barely moves (4.09 -> 4.02 Sv; Irminger and Labrador +0.8) but the Nordic box gets colder
  (-4.2 -> -5.5). **The Barents doesn't move (-13.7)**, even though its winter water is now as dense as the
  Nordic Seas' (coarse grid, 1028.2-1028.4 against 1028.0-1028.2).
- **B** (a site sinks no more than its heat loss can turn the arriving inflow into deep water): with the model's own
  air-sea exchange (`moc_lambda` x (t_in - t_eq) over the cell), and even counting the inflow cooled all the way to
  freezing, it binds on 4 of 85 northern sinking cells (0.38 Sv of 10.1; `scratchpad/laneA8/walin.py`). It would move
  almost nothing, so it was not written.
- **What locks the Barents** (`scratchpad/laneA8/nordic.py`, `depth.py` maps, Earth L6):
  1. `moc_sill` (300 m) treats the Barents shelf as a strait. On the L5 overturning grid the Barents is 230-300 m
     deep east of 30E (the Bear Island Trough 300-400 m), so it is `lid_d` and the inflow can't enter it at all.
     The rule was meant for Bering (40 m on that grid). Hudson Strait (216 m) is cut the same way.
  2. With the sill at 150 m (an experiment, not a fix) the inflow does reach the SW Barents (share 0.6-0.9) and it
     sinks there, but it arrives at -0.4 to +1 C (observed ~4-6 C at 20-33E), so the Barents stays frozen (-13.6).
     The branch only carries what sinks in the Barents itself (~1 Sv), so `_along` cools it within a cell or two.
     On Earth the Barents branch (~2 Sv) mostly flows on into the Arctic and sinks there (St Anna Trough).
  Sill 150 m with A: Fennoscandia -7.5, Iceland -8.9, Nordic -3.2, Barents -13.6.
- So the mechanism still missing is the ticket's own lead: the inflow past the sinking site, continuing poleward
  into a lidded Arctic where it becomes intermediate/deep water under the ice. The routing only sends water to
  cells that sink. And a shelf sea needs telling apart from a strait.

- [ ] rule: attempt 3 on (1) a shelf sea vs a strait for `moc_sill` and (2) an Arctic branch that sinks under the
  lid (the Atlantic layer), or park the Barents (option C)
- [ ] the Barents' coldest month within ~6 C of NCEP; Iceland no worse than -7.8
