# Screens for candidate 1 (herbs' roots respire; lane 123, PW-1261)

Patch: `candidate1-herb-root-resp.patch` (HERB_ROOT_RESP = 2.5 on the herb PFTs' rl). Not on the branch.

## Earth, observed climate, L6 (`npp_check.py`, world 506694)
See the table in `diagnosis.md`. x2.5: land NPP 54.6 Pg C/yr (59.6 before; target 45-70), potveg agreement 62.7% (61.7),
savanna 18.7 Mkm2 (21.6), burned 4.25 Mkm2/yr (5.67; GFED ~4.7), African grass ANPP at 626 mm 586 g dry (711; Deshmukh
512, Yang 397), herds 3.1 t/km2 at 550-700 mm (4.1; Coe 4.0-4.4).

## Tests (`uv run pytest -q -m "not slow"`, x2.5)
920 passed, 2 failed:
- `tests/test_vegetation.py::test_mediterranean_scrub_burns_and_stays_scrub`: the ideal Csa scrub's median fire return is 0
  (no fire in most cells; test wants 10-400 yr). Less grass means fine fuel below `FUEL_MIN` (250 g C/m2, tuned, no
  source). Threshold not touched (draft `draft-fire-fuel-threshold-after-grass-cue.md`).
- `tests/test_golden.py::test_golden_sim`: outputs change (expected for a model change; golden not updated since the
  patch is not merged).
At x3 the ideal-climate test also failed on one desert cell's cover (30.5% against < 30%; see diagnosis), hence x2.5.

## L6, 1 Gyr, seeds 1 and 2 (run with x3, the first setting; scratch data roots, deleted afterwards)
Last 200 Myr means (`tools/health.py::measure_run`):

| seed | variant | late dT C | arid % | trees % | land NPP g C | ice % | co2 (log stock) |
|---|---|---|---|---|---|---|---|
| 1 | base | -2.20 | 19.2 | 40.9 | 326 | 8.4 | -0.25 |
| 1 | herbs x3 | +2.56 | 20.0 | 48.0 | 381 | 2.4 | +0.46 |
| 2 | base | +1.80 | 22.1 | 46.5 | 418 | 2.3 | +0.30 |
| 2 | herbs x3 | +5.24 | 23.9 | 43.6 | 361 | 0.7 | +0.75 |

The runs warm by 3.4-4.8 C: the run's NPP sets the weathering factor (overview 2.18, "its NPP sets the weathering
factor"), so less grass growth means slower weathering, more CO2 and a warmer planet. That reference was calibrated on the
old, inflated grass NPP. Arid share and tree cover stay in band (health: 12-45% arid, 10-50% trees); the warming is the
blocker. Two seeds only: a pointer, not a pass rate.

## Verdict
C1 is the right plant mechanism (moves every grass biome toward field data on observed climate) but is **not mergeable
alone**: it needs (a) the weathering's NPP reference re-anchored so the carbon cycle doesn't read the plant fix as a
CO2 change, and (b) a sourced fire fuel floor. One strike counted against nothing: the candidate moved the plants right.
