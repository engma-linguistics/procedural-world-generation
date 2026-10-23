---
title: "The SH coasts' summer winds are still 2-3.5 m/s after PW-596 (Patagonia 3.4, Tasman 3.2, Agulhas 2.0): front_shift over the too-warm boundary currents and the sea's big-continent summer swing, so PW-593's summer layer still fails"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneA15
blocked_by: []
relates: [PW-593, PW-596, PW-594, PW-592]
refs: [planet/climate.py, docs/review/base-climate/laneA15/wind_after.txt, docs/review/base-climate/laneA15/patag.py, docs/review/base-climate/laneA15/pw596_probe_toggles.diff]
---

## Description
After PW-596 (lane A15), the NH summer westerlies are about right. The SH coasts' summer winds are not.

Summer wind speed (m/s), main -> A15; observed values as in PW-596:
- NE Atlantic 7.9 -> 6.6 (obs ~7); NE Pacific 8.7 -> 7.2 (obs ~6-7).
- Band 40-55: N 7.3 -> 6.2, S 6.5 -> 6.2. They are now equal; on Earth the SH's are faster.
- Off Patagonia 3.1 -> 3.4 (obs ~8-10), Tasman 3.5 -> 3.2 (~7), Agulhas 2.3 -> 2.0 (~7).

Where it comes from (`laneA15/wdiag.py`, `patag.py`):
- **Patagonia.** The belts alone give 5.2 m/s, or 5.9 without `front_shift`. The land-sea part takes them to
  3.4. That is not Patagonia's own thermal low (anomaly +1.0 C, already cut by `low_column`). It is the **sea's**
  first-guess summer anomaly off the coast, +1.9 C: `_sea_half`'s land part gives the sea a big continent's swing
  (`continental x s x land_air`) whatever the land's width (`draft-sea-swing-land-part-is-a-big-continents.md`).
  - Tried (`X_COL=3` in `pw596_probe_toggles.diff`): weighting `land_air`'s source by `low_column`.
  - Patagonia's half-swing 6.1 -> 4.8 and the SH coastal range 12.3 -> 11.5, but W Europe warmest -0.9 -> -1.5,
    Biscay-N Sea -2.5 -> -3.9, near-land NH swing within 1.5x 52 -> 43%.
- **Tasman and Agulhas.** The belts alone give 2.7 and 1.8 m/s. `front_shift` puts them at a lower "air-mass
  latitude", because their SST is too warm (+4.7 / +2.4 C summer; PW-594's western boundary currents). Without
  `front_shift` they would be 3.9 and 2.1. So part of it is PW-594, and part is that the model's mean-vector wind
  is calm in the horse latitudes, where the observed scalar wind (with its transients) is ~5-7.

PW-593's wind-set summer layer (`ml_wind`, re-applied on A15's winds; `p3_*_ml*.txt` in the lane's stages
section) therefore still fails:
- rain r 0.607;
- SH coastal range 14.7;
- Patagonia half-swing 8.6 (obs 3.7);
- Tasmania warmest +8.8.

It does fix the NH: near-land N within 1.5x 52 -> 75%, NE Atlantic half-swing 1.7 -> 2.8 (obs 3.2) with the
final winds (`ml_wind=2`).

Next, in order:
1. PW-594: the warm SH boundary currents, which also feed `front_shift`'s calm.
2. The sea swing's land part by the land's width, without W Europe's regression. The NE Atlantic's sea air may
   need the overturning's winter side first (PW-592).
3. The stirring wind for the summer layer as a scalar speed with the storms' transients: A14's storminess
   term, re-tried on the new winds.
4. Then `ml_wind` again.

- [ ] SH 40-55S summer winds faster than NH 40-55N; SH coastal summer winds not under ~5 m/s
- [ ] PW-593's summer layer passes rain r >= 0.617 and the SH coastal range <= 12.5
