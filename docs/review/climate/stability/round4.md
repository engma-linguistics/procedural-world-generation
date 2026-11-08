# Climate stability, round 4 (lane 187, 2026-11-04): L7's carbon-cycle yardstick measured (PW-1458)

**In plain words.** Each grid level has one fixed carbon-cycle yardstick (`earth.YARDSTICK`, D47 / PW-1424 A). L7's
value, 1.542, was not measured. Lane 170 derived it from six older L7 store runs, made before D47 and before lane 181's
canopy-respiration change (KN_RESP 0.4). This lane measures it on current main by spinning stock L7 draws to 300 Myr,
the point where every run's yardstick is learnt, and re-checks L6 the same way. Each 0.1 the constant is off moves
every L7 world's later climate about 1.1 C, all in the same direction.

## Method
- Code: a frozen copy of main 78140574 (`git archive`). `planet/` is unchanged since lane 181's merge (98547e1e),
  so this is D47 + KN_RESP 0.4.
- L7: `fork.py spin` (docs/review/base-climate/v1-finish-16/) to 300 Myr, stock settings (`star_brightening=1.0`,
  `climate_offset=0`), 1 thread each, 6 at once. Draws are lane 170's eight judge seeds plus seeds from
  `random.Random(187)` (the draw list is in scratch `l187/draws7.txt`). The pin only acts after 300 Myr
  (`earth.REF_FREEZE`), so a spin to 300 Myr measures the learnt yardstick with no pin. `tools/yardstick.py` reads it.
- L6: lane 181's `kn` arm (36 straight 1-Gyr `paired.sh` runs of exactly this physics, scratch `l181/judge/kn_*`)
  already holds every draw's learnt y at 300 Myr. `tools/yardstick.py` reads it there, so no new L6 spins were
  needed. It is compared against lane 170b's `cand` spins of the same 36 draws (D47 without KN_RESP), which set 1.377.

## L6 (36 draws, current code)
- Learnt y mean **1.337**, sd 0.143, standard error 0.024. YARDSTICK[6] is 1.377 (standard error 0.035).
- Paired against lane 170b's spins of the same draws: KN_RESP shifts y by **-0.040** (paired sd 0.189, standard
  error 0.031), which is 1.3 standard errors. Unpaired, the two means differ by 0.040 with a joint standard error of
  0.042.
- Verdict: within error. L6 stays at 1.377.

## L7 (24 draws, current code; lane 187b)
- Learnt y mean **1.618**, sd 0.178, standard error 0.036, against YARDSTICK[7] 1.542 (+0.076, 2.1 standard errors).
  Range 1.327 (seed 267766) to 1.842 (seed 35471). Scratch `l187/l7_y_24.txt`.
- Verdict: re-fit. **YARDSTICK[7] = 1.618** (`planet/tectonics/earth.py`). L6 stays at 1.377.

## Paired check (lane 187b): the same 300-Myr spins continued to 1 Gyr under 1.542 (old) and 1.618 (new)
Four draws picked across the y range (low 267766, middle 170889 and 53669, high 35471). Each spin was continued
twice from its 300-Myr checkpoint (`cont_one.sh main|new SEED`, 1 thread each). The two copies of the code differ
only in YARDSTICK[7], so every difference below is the yardstick's. Baseline in every row: the same draw on the old
YARDSTICK[7] 1.542. Late = 600-1000 Myr, as `tools/judge.py paired`.

| draw (learnt y) | late dT old | late dT new | new - old | late CO2 index old / new | end T vs 13.8 C old / new | end pCO2 old / new |
|---|---|---|---|---|---|---|
| 267766 (1.327) | +3.02 | +3.88 | +0.86 | +0.83 / +0.97 | -0.6 / -0.9 | 318 / 268 |
| 170889 (1.529) | +0.12 | -0.21 | -0.33 | +0.53 / +0.45 | -0.2 / -1.2 | 558 / 390 |
| 53669 (1.627) | +2.75 | +1.91 | -0.84 | +0.88 / +0.73 | -3.9 / +2.8 | 288 / 494 |
| 35471 (1.842) | +4.09 | +0.70 | -3.39 | +1.15 / +0.68 | +2.3 / -0.4 | 528 / 377 |

- Late dT: paired median -0.59 C (95% interval -3.39 to +0.85, 3 of 4 cooler). The expected shift is about
  -0.84 C (0.076 x 1.1 C per 0.1). With 4 draws the interval holds 0; the direction and size are as expected.
- The sink's reference moves by exactly -0.076 in ln on every draw (the change itself); the source's is unchanged.
- Hard failures, both arms (`tools/hard_bar.py`): frozen over 0/4, boiled 0/4, ocean loss 0/4, CO2 crash (below the
  plants' compensation point) 0/4; CO2 under 100 ppm 0/4. Lowest pCO2 old 122-406, new 142-222 ppm. End pCO2 inside
  180-600 on all 8 runs.
- Soft passes (bar + finish moment): 4/4 both arms. Icehouse 4/4 and glacial maximum 2/4 in both.
- Single-draw end temperatures swing several degrees either way (53669: -3.9 to +2.8) while the late means move
  less: chaos, not signal, at one draw (the late-window mean is the measure).

## Checks (lane 187b)
- `NUMBA_NUM_THREADS=3 uv run pytest -q -n 2 -m "not slow"`: 1018 passed, 1 skipped (goldens included, unchanged:
  the goldens and simulated test grids are all below L7, which still take L6's 1.377; test_co2_stock reads YARDSTICK[7] by name). Slow climate files
  (test_envelopes, test_sea_level, test_soils) plus test_co2_stock and test_golden: 39 passed, 1 skipped.
- `tools/scorecard.py` (L6 seeds 1 and 2, and the Earth climate): every number identical to the previous line
  (38073e05), as expected: the change acts only at L7. `tools/earth_check.py` (L6, dT 0): global mean T 13.9 vs
  NCEP 14.0 C, rain 997 vs GPCP 983 mm/yr; it does not use the carbon cycle.
- Not done: a 36-draw L7 paired judge. 4 draws give the direction (3 of 4 cooler) and 0 hard failures, not a pass
  rate.
