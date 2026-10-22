# Lane A handoff A6 (2026-10-22, ~100 tool calls)

## State of the branch
- Main 564350b is merged in. PW-575 (step 1) is commit abe4838 on this branch (pytest passes, goldens regenerated, scorecard line added): see stages.md, "PW-575: the winter winds (lane A6)".
  Its bar is **not** met (Fennoscandia −8.9 C against ±6; the Nordic Seas box unchanged), for reasons that lie in the
  ocean north of 72N (`issue-tracking/inbox/draft-nordic-winter-barents-frozen.md`). The coordinator rules whether
  it merges as an improvement.
- Experiment switches (not on the branch): `.../scratchpad/laneA6/exp_switches.diff` (applies on 564350b's
  `planet/climate.py`). Probes: `.../scratchpad/laneA6/probe.py` (earth_check rain + climate_bias rows + Nordic winds,
  one Earth L6 climate per variant, ~8 s each), `pr.sh` (runs it in the worktree), `trace.py` (a parallel),
  `grid2.py` (a bias map), `cdiag.py` (winter cloud and North Atlantic boxes), `wdiag.py` (the winds split into belts
  and land-sea part, with the model's and NCEP's January temperatures).
- Steps 2 (PW-579) and 3 (stage 3) are not started in code. Notes for both below.

## Step 2: PW-579, entrainment (the owner's ruling: model it)
What the code does today (`ocean.overturning`): per sea and hemisphere, `ref` = the area mean of the densest
`moc_top` (10%) of the polar sea's winter density, less `moc_mix` (0.5 kg/m3, "mixes on its way down"). Cells within
`moc_drho` (0.3) of `ref` can sink (`gate`), with Stommel's flow `moc × gate × dr × area`, then capped per sea at
`moc_k × (ref + moc_mix − rho_rep)`.

Two things to keep in mind when writing the entrainment term:
- `moc_mix` already *is* the entrainment's effect on density (the plume is made lighter on its way down). Taken
  literally as mixing with ambient polar water (ρ_a ≈ 1027.0 on dad91b, pocket ρ_s ≈ 1029.5), it only grows the volume
  by (ρ_s − ρ_a) / (ρ_s − moc_mix − ρ_a) ≈ 1.25×. That isn't the few Sv the bar wants. So the volume must come from
  entraining a fixed multiple of the source (observed overflows roughly double to triple downstream: Denmark Strait
  ~3 → 5–6 Sv, Weddell shelf water ~1–2 → 4–5 Sv), or from letting the entrained ambient water define the deep water.
- The cleaner form, I think: the plume (source V_s at ρ_s) entrains ambient polar water (the hemisphere's open polar
  sea, area-mean ρ_a) in a ratio E, so the deep water it forms is V_s (1 + E) at ρ_d = (ρ_s + E ρ_a) / (1 + E). Use ρ_d
  (not the pocket's own densest 10%) as `ref`, so the rest of the open sea within `moc_drho` of ρ_d sinks too; the
  pocket's own flux is multiplied by (1 + E). This is options A and B of the ticket together, and it can only raise a
  hemisphere's sinking relative to today's pocket case. On worlds without a pocket (ρ_s ≈ ρ_a) it changes nothing.
  E would be a new constant from the observed overflows (~1–2), so say so.
- The cap (`moc_k × (ref + moc_mix − rho_rep)`) then needs ρ_d's analogue; check `test_meltwater_weakens_the_overturning`
  (it was a knife edge at the cap) and `test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast` (the time
  zoom's ice ages react strongly to a few % of overturning, stages.md lane A5).
- Bar: every generated world's south a few Sv or more (dad91b is 0.86 Sv after PW-575), Earth's Weddell / Ross
  plausible (2.4 Sv now). Re-run `tools/overturning_report.py --earth --world <the 9>`.

## Step 3: stage 3 (PW-352, PW-457, PW-573)
- PW-575 made the *winter* air over land relax in time (`air_m` against `ice_b`). The summer still relaxes over a fixed
  `air_km_s` (450 km). Making the summer per time as well, with the summer's own (convective, sensible-heat) exchange,
  is PW-573's mechanism: small lands in strong westerlies keep the sea's summer. The winter change alone moved the SH
  coastal seasonal range 16.3 → 14.3 (NCEP 9.6). See `draft-air-relaxation-in-time-summer-and-mountains.md`.
- PW-352 / PW-457: the humid east coasts' summers are already too warm in the first pass (`_air_temps`), so a Bowen
  split on its own won't reach them (PW-352's update). Measure with `probe.py`'s "summer" row (warmest-month bias by
  observed summer rain) and the review's bars.
- Western Europe's winter is now near right (London's coldest month −3.2 → +1.6, obs 4.7; Paris 2.8 vs 2.4), so stage 3
  starts from a better winter.
