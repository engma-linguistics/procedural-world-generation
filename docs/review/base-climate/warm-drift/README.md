# Lane 24: why more land runs warmer after the weld fix (PW-980), PW-880 and PW-819 checked (2026-10-29)

## Verdict
- **PW-880 and PW-819 are already on main and they work. Nothing left to change.**
  - PW-880 (1b52cdf): the sink reads `sim.npp_w`, the plants grown at PCO2_BALANCE. Over the paired set (36 draws,
    600-1000 Myr), the planted sink's CO2 log-slope (diag `w_a`) is 0.176, with a bare share of 0.083. That is FERT's
    0.2, a little saturated above the balance, with no extra ~0.11 from the NPP.
  - PW-819 (e6439ee1, sized in v1-finish-13): the drift sits on the carbon source, and nothing in the target is a
    temperature term. corr(dT, ln CO2) after 300 Myr has a median of +0.68 and is below 0 on 1 of 36 draws.
- **Why the finish is warmer after the weld fix.** It is the carbon cycle, through the erosion supply, measured
  against the sink reference frozen at REF_FREEZE (300 Myr). It is not the land area, the land albedo (dT has no land
  albedo term), the land's heat or PW-880. Paired medians of the per-draw differences, pre-weld 3f43093d against main
  b711afe6, 18 draws at roll 0.001, `decomp.py`:

| term (ln unless noted) | pre-weld | main | median paired diff |
|---|---|---|---|
| erosion supply 250-300 Myr (learnt into the sink reference) | 5.19 | 5.33 | **+0.22** |
| sink reference | 6.71 | 6.82 | **+0.11** |
| erosion supply 800-990 Myr | 5.21 | 5.18 | -0.08 |
| source, raw / against its reference | 7.99 / +0.01 | 7.89 / -0.10 | -0.09 / -0.06 |
| CO2 (e-folds), 800-990 Myr | 0.33 | 0.70 | +0.22 |
| dT (C), 800-990 Myr | 1.26 | 2.36 | +0.84 |
| land share | 0.312 | 0.347 | +0.040 |

- Main's spin-up erodes more (median supply by 100 Myr bin: 189/202/199 against 182/188/185 before the weld fix).
  The sink reference learns that. Later, main's supply per land area falls (ln -0.11; before the weld fix +0.05).
  So, against its frozen reference, the planet weathers ~19% less and holds ~0.2 e-folds more CO2. Across main's
  draws, late CO2 correlates -0.62 with the late/spin-up supply ratio and -0.23 with the land change (`corr.py`).
- Land enters the sink only through erosion. The new land is low and flat, so it adds almost no sink: that is why
  "more land weathers more" doesn't happen here (draft-weathering-land-area-term.md). The climate's own land effect
  is the other way: at fixed dT the true mean is -0.25 C for +3.5 points of land (`off.py`, main's steps after
  300 Myr).
- **How much of it is chaos.** A near-null change (below) moves 15 of 36 draws, the pooled count by ±3 and the median
  end T by ±0.8 C. Lane 23's 31 -> 28 and its +0.9 C fall inside that band. What is systematic is the land (+4
  points, +1.5 of it at 300-400 Myr) and the sink reference shift (+0.11, about twice the null change's ±0.05).
  Draft: draft-paired-judge-chaos-floor.md.
- Still open (PW-980): why main's spin-up erodes about 20% above its late run (it stays flat before the weld fix),
  and how to bring the land back to 29-33% (shelves, PW-950, v2).

## Change 1: water conservation for the continents' sea (`earth.continent_water`)
- Sea level was only the ocean floor's age (and the ice). Continents could rise out of the sea without their water
  going anywhere. Now the sea the start's continents hold, at the ice-free level, is the reference. Water given up
  (or taken back) raises (or lowers) the basins by 0.69 of its depth over the ocean, as the basins' own term does.
  Shelves an ice age drains are not counted, since sea_ice already took that water. It is part of `sea_tect`
  (`sim.sea_cont`, recorded by the diag).
- Measured at L6 it is small and negative: a median of -15 m late (range -27..-4 m). The continents hold a little
  *more* water as margins rift and drown, so it does not bring the land back: land +0.15 ± 0.8 points per draw.

Paired judge (L6 1 Gyr, v1-finish-16's 18 draws × rolls 0.0005 / 0.001, `paired.sh` and `judge.py`; pass = a good
finish moment and no hellhouse):

| arm | r0.0005 | r0.001 | pooled | icebox | hellhouse | median end T |
|---|---|---|---|---|---|---|
| main b711afe6 | 15/18 | 13/18 | **28/36** | 10/36 | 0 | +0.85 C |
| branch (continent_water) | 16/18 | 13/18 | **29/36** | 13/36 | 0 | +1.63 C |
| pre-weld 3f43093d (r0.001 only) | | 16/18 | | 3/18 | 0 | -0.13 C (that roll) |

Paired: 21 pass in both arms, 7 on main only, 8 on the branch only, 0 in neither. No SIM SUSPECT: iceboxes are 36%.
Main reproduces lane 23's branch exactly (28/36, +0.85 C).

## Scorecard and earth_check (branch)
- `tools/scorecard.py` (L6 seeds 1 2, 1 Gyr), line appended to docs/scorecard.jsonl:
  - Earth: group 71.2%, exact 33.9%, log-rain corr 0.648.
  - Seed 1: land 36.2%, shelf 1.5%, submerged median -1025 m.
  - Seed 2: land 35.3%, shelf 1.4%, submerged median -902 m.
  - Main's example runs of the same seeds: land 33.4 / 33.1%. Those two seeds sit in the tail of the ±0.8-point
    per-draw spread.
- `tools/earth_check.py --level 6`: main group 71%, exact 34%, log-rain corr 0.648. This is unchanged: the change
  doesn't touch the climate on fixed geography.

## Example runs (main checkout's store, L6 1 Gyr, default params, `examples.sh`)
- warm-main-s1: 17a285 (land 33.4%)
- warm-new-s1: 2d1dea (36.2%)
- warm-main-s2: 54649a (33.1%)
- warm-new-s2: 22f511 (35.3%)

## Harness (here)
- `paired.sh`: the judge launcher; any code dir; lane cap 12.
- `judge.py`: the paired table, plus 600-1000 Myr and 250-300 Myr term medians.
- `decomp.py`: the late CO2 balance split into source, reference, supply, climate and plants, paired.
- `bins.py`: per 100 Myr bin medians.
- `corr.py`: per-draw correlations of late CO2.
- `off.py`: the true mean T against land at fixed dT.
- `examples.sh`.
