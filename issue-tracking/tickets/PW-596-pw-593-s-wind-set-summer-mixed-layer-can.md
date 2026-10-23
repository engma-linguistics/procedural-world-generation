---
id: PW-596
title: "PW-593's wind-set summer mixed layer can't work on the model's summer winds: the westerly belts have one strength in every season and hemisphere, and the land-sea part slows the SH coasts' summer westerlies to 2-3.5 m/s"
type: task
status: done
parent: PW-470
milestone: v1
subsystem: climate
effort: l
impact: high
found_by: base-climate-laneA14
blocked_by: []
relates: [PW-593, PW-589, PW-573, PW-575]
refs: [planet/climate.py, docs/review/base-climate/laneA14/, docs/review/base-climate/stages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A14 built PW-593's mechanism: the summer half of the sea's swing goes into a Monin-Obukhov layer,
h = u*^3 / (kappa g alpha Q / rho c). It uses the model's own summer wind (u* from the bulk stress, C_D 1.3e-3),
the summer's extra sunshine Q (as `_sea_half` has it) and the water's thermal expansion at its summer temperature
(from `ocean.density`). The depth is clipped between `light_m` 20 m (sunlight's depth) and `brine_m` 50 m. The
winter side is unchanged. The diff is `docs/review/base-climate/laneA14/pw593_attempt1_toggles.diff` (`ml_wind=1`).

**It fixes the NH and breaks the SH, because the model's summer winds are the wrong way round.** Summer wind speed
(`v_sum`, m/s; `laneA14/wind_base.txt`) against typical observed scalar summer winds:
- NE Pacific 40-50N 8.7 (obs ~6-7), NE Atlantic 7.9 (~7).
- Off Patagonia 3.1 (~8-10), Tasman 3.5 (~7), Agulhas 2.3 (~7).
- The 40-50 band: N 7.3, S 6.4. On Earth the SH's summer westerlies are much stronger than the NH's.

Two causes, both in the winds:
1. `wind()`'s westerly belt has one strength (1.0 x U_REF at 48 deg) in both seasons and both hemispheres. With the
   land-sea part left out, the belts alone give 6.2-7.0 m/s at NE Pac / NE Atl / Patagonia alike. The real surface
   westerlies are eddy-driven: they scale with the season's baroclinicity, which `jet_stream` already computes. So
   NH summer winds are weak and the SH's stay strong all year.
2. `monsoon_wind`'s land-sea part slows the SH coasts' westerlies: Patagonia 6.4 → 3.1 m/s, Tasman 4.3 → 3.5. It
   treats narrow summer-warm lands like continents (the same smoothing over ~900 km). It also speeds the NE
   Pacific up, 6.2 → 8.7.

Because the depth goes as U^3, the layer turns those errors into swing errors. Earth L6, main → `ml_wind=1`
(`laneA14/p3_attempt1.txt`):
- W Europe warmest month −1.2 → **−0.1**. NH near-land sea swing within 1.5x of NCEP 52 → 69%, NH open sea
  10 → 35%. Fennoscandia warmest −3.9 → −0.7.
- But rain r 0.620 → **0.598** (bar ≥ 0.617). SH coastal range 12.4 → **14.6** (bar ≤ 12.5). SH near-land swing
  within 1.5x 54 → 40%. Patagonia sea half-swing 6.2 → 8.7 (obs 3.7), Tasmania warmest +6.0 → +8.9, Iceland
  +3.2 → +8.2, humid summers about 1 C warmer.
- Offline (`laneA14/ev.py`, `ev2.py`): no floor, coefficient or storminess term rescues it. The NE Pacific stays
  50 m deep under its 8.7 m/s, and the calm SH coasts always reach the floor.

Options:
- A (lean): **winds first.** Make the westerly belts' strength follow each season's own meridional temperature
  contrast (the eddy-driven jet, from `jet_stream`'s baroclinicity), and re-check the land-sea part over narrow
  lands. Then re-run the saved `ml_wind` diff on those winds. This is a winds-lane change: it touches rain,
  currents and the winter carry (PW-575 / PW-026), so it needs its own measurement pass.
- B: merge the summer layer with the stirring taken from the zonal belts only. Rejected: it ignores the model's
  real winds, and the belts have no hemispheric contrast either, so it would be a flat ~40 m layer in disguise.
- C: park PW-593 and accept W Europe's −1.2 until the winds' stage.

- [ ] rule A / B / C
- [ ] (A) summer westerlies by season and hemisphere: SH 40-55S summer faster than NH 40-55N summer; SH coastal
      summer winds not under ~5 m/s

## Updates
- 2026-10-23: Status needs-decision -> done. Merged (A16 98749b4 + merge): westerly belts per season and hemisphere from that season's 30-65 deg contrast; thermal low as deep as the column share its warmth fills. With A17's island walls (PW-594 part 1). Earth: rain r 0.620 -> 0.630, Koppen group 70 -> 71, Fennoscandia coldest -4.5 -> -2.8; stage-1 overturning holds. Full pytest green on main dc2e54e. SH coastal summer winds still calm: PW-626.
- 2026-10-23: Created from inbox draft draft-summer-mixed-layer-needs-seasonal-winds.md (found by base-climate-laneA14).
