---
title: "PW-582 attempt 1: the Barents stays frozen (-13.7 C) because it never sinks, so no inflow is routed to it; Iceland -10.3 against the -7.8 bar"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: ocean
effort: l
impact: high
found_by: base-climate-laneA7
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

- [ ] rule on A / B / C
- [ ] the Barents' coldest month within ~6 C of NCEP; Iceland no worse than -7.8
