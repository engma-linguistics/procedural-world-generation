# Lane A handoff A3 (2026-10-22, ~95 tool calls)

## State of the branch
- Branch `worktree-agent-a4338f1afd47c88b2`. Main 2684f2b is merged in.
- `f1e1600` lands stage 2's attempt 2. `cb3ecd8` and `dc5a809` add the record (stages.md "Stage 2b") and the inbox
  draft `draft-stage2b-landed-rain-regression.md`, which goes into PW-578.
- The coordinator's ruling: stage 2b stays on this branch and merges together with the rain fix (PW-578), once
  `uv run pytest -q` passes with the tests unchanged.
- Three tests fail on stage 2b alone:
  - `test_earth_climate_score` (Köppen 65.7 against a floor of 66);
  - `test_same_planet_rains_the_same_at_two_levels` (5.02% against 5%);
  - `test_zoom_soils::test_zoom_soil_layers` (floodplain wet share 0.48 against > 0.5). If it is the only one left
    failing, report what drives the alluvium share; don't touch it.
- PW-575's wind experiments are parked on branch `laneA3-winds-wip`. They are switches only, for after PW-578.
  The finding: the first-guess t_sl has no Icelandic low, but the finished climate's January temperatures do.

## PW-578, the rain fix: attempt 1 of 3 (experiment only; nothing in `planet/` yet)
Done in an experiment copy of the package:
- `.../scratchpad/laneA3/mkexp.py` builds `.../scratchpad/laneA3/exp/` from the branch's `climate.py`, with TUNE
  switches `x_form`, `x_A`, `x_c` and `x_B`.
- Scores come from `exp/rscore.py` (earth_check.analyse) and `exp/tools/climate_bias.py --set ...`.

**Mechanism (the coordinator agreed it is the error):** in attempt 2 one half-swing,
`s × (sea_half + continental × land_air)`, serves both the sea's air and its water. Two things are wrong with that.
1. The water takes only part of the land air's swing. The air-sea exchange (`open_b`, 30 W/m2/C) works against the
   mixed layer's seasonal heat capacity, ρ c h ω ≈ 4.1e6 × 50 m (`brine_m`) × 2e-7 ≈ 41 W/m2/C. So the coupling is
   c = open_b / (open_b + ρ c h ω) ≈ 0.42, derived from existing quantities. The winter air's own cold is already
   carried separately (`_winter_air`), so the water swing can be used everywhere.
2. The open ocean's own swing is about ±3 C outside the tropics at every latitude. Observed open-ocean ranges are
   5.7 / 6.0 at 20–35 / 35–50 deg. Higher latitudes get more seasonal sun, but deeper mixed layers offset it. So the
   own swing is not a constant times s.
   - Tried as `own = 3.0 × min(1, s / 0.5)` C.
   - This form is still a guess. A derivation would be the seasonal sun over (ρ c h(lat) ω + feedback), with h
     from the wind or storminess. The Southern Ocean needs a smaller own swing than this.

**Results, Earth L6** (log-rain r / Köppen group / summer share):

| variant | r | group | summer | notes |
|---|---|---|---|---|
| attempt 2 (branch) | 0.533 | 66.4 | 0.80 | |
| c = 0.42, own 1.9 × s | 0.577 | 68.1 | 0.78 | |
| c = 0.42, own 3 C flat (**F1**) | 0.590 | 69.0 | 0.78 | sea-ice bar holds (below) |
| F1, own 3.5 | 0.592 | 69.2 | 0.78 | |
| c = 0.3, own 3 flat | 0.599 | 69.7 | 0.77 | |
| F1 with the winds' t_sl on 6 × s | 0.590 | 68.9 | 0.78 | so the winds no longer matter |
| uniform 6 × s, c = 0 | 0.615 | 70.2 | 0.75 | southern ice +37%: fails the bar |

**F1's stage-2 bar** (climate_bias, coldest month; all lines pass):
- Hudson Bay −18.9, Baffin Bay −20.6, Okhotsk −7.0;
- the Antarctic pack's bias −2.1;
- the winter sea-ice proxy N / S 19.0 / 22.8 against 16.8 / 20.2 (+13% / +13%);
- Labrador +3.7, the Hudson Bay lowlands +5.4;
- also Baffin Bay's summer +8.7 → +3.5 (PW-577 item 2, nearly fixed) and the Nordic Seas' coldest month
  −10.4 → −9.3.

The overturning, generated worlds and pytest were not yet run on F1.

## Next steps
1. Find the rest. The rain still prefers coastal water that doesn't swing: a lower c scores better, and the summer
   share is 0.77–0.78 against 0.75.
   - The suspect is `src_q` over seas next to land in summer feeding the monsoon. With a land-coupled swing, a hot
     coastal summer sea fills the air to `rh × qsat(sst)` at once, the instant fill parked in PW-015.
   - Bisect by region and season: give `qs` / `src_q` the old swing only where `land_air > 0.3`, or only in the
     summer half.
   - Then re-derive that piece rather than re-tune it.
2. Make the own swing physical (above), then put F1's form into `planet/climate.py`:
   - in `compute`: `sea_half = own + s × c × continental × land_air`, with c from `open_b` and `brine_m`;
   - update TUNE's `sea_half` comment.
3. Then the full bar: pytest unchanged (the three tests above), earth_check, climate_bias, overturning_report on Earth
   and the 9 worlds, the scorecard, the generated worlds' rain (`.../scratchpad/laneA3/wrain.py`), and a section in
   stages.md.

Attempts used on PW-578: 1 of 3 (the c / own-swing split).
