---
id: PW-626
title: "The SH coasts' summer winds are still 2-3.5 m/s after PW-596 (Patagonia 3.4, Tasman 3.2, Agulhas 2.0): front_shift over the too-warm boundary currents and the sea's big-continent summer swing, so PW-593's summer layer still fails"
type: task
status: todo
parent: PW-570
milestone: later
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneA15
blocked_by: []
relates: [PW-593, PW-596, PW-594, PW-592]
refs: [planet/climate.py, docs/review/base-climate/laneA15/wind_after.txt, docs/review/base-climate/laneA15/patag.py, docs/review/base-climate/laneA15/pw596_probe_toggles.diff]
created: 2026-10-23
updated: 2026-11-03
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

## Lane A17 (steps 1-3 of the list above, Earth L6; `docs/review/base-climate/laneA17/`)
Summer winds (m/s) A16 branch -> step 1 (New Zealand walls the gyres) -> step 2 (stable summer off-land air,
`draft-stable-summer-off-land-air.md`): off Patagonia 3.4 / 3.4 / 3.4, Tasman 3.2 / 3.4 / 3.6, Agulhas 2.0 / 2.0 /
1.9, NE Atlantic 6.6 / 6.6 / 5.9; band 40-55 N / S 6.2 / 6.2 -> 5.9 / 6.1. **They did not come up.**
- Off Patagonia step 2 took the sea's first-guess summer anomaly from +1.9 to -0.2 C, but the wind stayed 3.4: the
  belts give 5.4 there, and Patagonia's own low still costs -1.4 m/s east through the 900 km part (land anomaly +1.1
  even after `low_column`; its 900 km smoothing +0.4 reaches the coastal sea). The belts alone, 5.4, are short of
  the observed 8-10 too.
- Tasman and Agulhas: the belts alone are 3.1 and 1.8 (they sit in the horse latitudes); `front_shift` costs
  0.8 / 0.3 after step 1's cooler Tasman. The calm is the mean-vector wind's, not the warm currents'.
- Step 3, the storms' transients in the stirring wind (u^2 = |U|^2 + (ml_storm x storminess x U_REF)^2, on step 2
  with `ml_wind`; `laneA17/bars_pw593_on_step2.md`):

  | | step 2 | + ml_wind | + ml_storm 0.5 | + ml_storm 1 |
  |---|---|---|---|---|
  | SH coastal range (<= 12.5) | 12.1 | 14.5 | 14.2 | 13.2 |
  | W Europe warmest | -2.1 | +0.2 | -0.5 | -1.9 |
  | Biscay-N Sea sea summer | -5.4 | -0.9 | -2.5 | -4.7 |
  | near-land swing in 1.5x N / S | 33 / 69% | 69 / 46% | 65 / 48% | 50 / 56% |
  | half-swing NE Atl / Pat / Tasman (obs 3.2 / 3.7 / 2.7) | 1.7 / 4.8 / 3.1 | 3.1 / 6.9 / 4.8 | 2.7 / 6.7 / 4.8 | 1.8 / 5.8 / 3.8 |

  The transients deepen both hemispheres' layers alike (the summer storminess is about equal), so they take back
  the NH's gain before they fix the SH. Rain r stays 0.649 (the layer acts on the final winds only).
- So `ml_wind` still fails. What the SH coasts lack is neither the warm currents nor the transients: it is the
  summer belts' own SH strength (S summer belt 0.91 of the mean, 5.4 m/s off Patagonia, SH 40-55 no faster than NH)
  and a thermal low over narrow land that still reaches the sea. Next candidates: the SH summer belt's contrast
  (westerly_belt reads 30-65 deg; the SH summer storm track's contrast sits at 45-60 over open sea), and
  `monsoon_wind`'s 900 km part over land narrower than the smoothing.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Created from inbox draft draft-sh-coastal-summer-winds-still-calm.md (found by base-climate-laneA15).
