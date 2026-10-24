# v1-finish-7: PW-761, C′: a brightening star on the model's own thermostat (2026-10-24)

Branch `worktree-agent-a8c9bf545b52522e5`, from main 9ffdbe6.

The thermostat is within the literature's range and is unchanged. A Sun-like star at Gough's rate warms the runs to
ice-free. The owner's lever (2026-10-24), a slower-brightening star chosen within the plausible range, does pass
the bar:
- `star_brightening` = 0.45 times the Sun's rate, a K-type star of ~0.75 solar masses;
- 16/18 L6 draws pass, the icehouse median is 20%, and the history is flat (early 14%, late 16%);
- it is now the default.

**Report it as a chosen star, not a derived one.** It is the one free number in this change.

## Numbers first (L6, 1 Gyr, judged on 300-1000 Myr, v1-finish-5's 18 seed-draws, same bar and harness)

Bar: icehouse share <= 40%, no always-icebox, no hellhole (`passrate.py` from v1-finish-6, unchanged). Never-ice
(< 5%) and the median dT are reported only. Deep ice is the mean % of climate updates with ice below -150 m of sea
level.

| config | pass | icehouse median | early / late (300-500 / 600-1000) | always-icebox | never-ice | hellhole | dT median | deep ice |
|---|---|---|---|---|---|---|---|---|
| base (PW-741; v1-finish-6's row) | 5/18 (28%) | 46% | 24 / 57 | 2 | 0 | 0 | +1.1 | 12% |
| **C′**: Gough star as young as the planet, the model's 0.81 C per W/m2 | 18/18 | 0% | 0 / 0 | 0 | **16** | 0 | +7.8 | 0% |
| C′ at v1-finish-6's 0.6 C per W/m2 | 17/18 | 3% | 0 / 3 | 0 | **11** | 0 | +6.0 | 1% |
| star 0.20 x Gough | 12/18 (67%) | 30% | 8 / 36 | 1 | 3 | 0 | +2.9 | 6% |
| star 0.30 x Gough | 12/18 (67%) | 26% | 2 / 35 | 1 | 2 | 0 | +3.3 | 8% |
| **star 0.45 x Gough (now the default)** | **16/18 (89%)** | **20%** | **14 / 16** | **0** | 3 | 0 | +4.1 | 5% |

Showcase seeds, L6 offset 0, icehouse % for 957317 / 619496 / 583167 / 639472:
- base: 45 / 10 / 11 / 82;
- 0.45: 3 / 7 / 1 / 24.

The never-ice draws at 0.2-0.45 are the base's warm seeds (583167, 733847, 958504; 1-5% icehouse). The bar
doesn't count them. They are greenhouse worlds with brief ice, not a new failure mode, but see the draft.

18 draws have a sd of ~11 points: 0.2 and 0.3 (67%) can't be told apart from each other, and 0.45 (89%) is better than
both only at about 1.5-2 sd. 0.45 is also the only rate that removes the late trend (late 16% against early 14%).

L7 (the owner's main level), 4 showcase seeds x 2 draws, code default (0.45): **7/8 pass, icehouse median 25%**,
no icebox, no never-ice, no hellhole (base 3/8, 45%). See "L7" below.

## 1. The thermostat: in range, so not changed

Where it is set (`planet/tectonics/earth.py`):
- **Temperature dependence.** The sink is `supply x exp(WEATHER_K (T_local - 15)) x plants`, with WEATHER_K = 0.09
  per C. That is an Arrhenius e-folding of ~11 K, Ea ~63 kJ/mol at 288 K. Lab and field silicate Ea is
  ~40-80 kJ/mol (Brady 1991; White & Blum 1995; West et al. 2005), so ~8.6-17 K: **in range**.
- **CO2 dependence.** The stock settles at X^WEATHER_CO2 = source / sink, with WEATHER_CO2 = 0.4. The literature
  range is 0.2-0.5 (Walker et al. 1981 0.3; GEOCARB 0.5 abiotic; Krissansen-Totton & Catling 2017's prior and
  posterior 0.2-0.5): **in range**.
- **CO2 forcing.** co2_sensitivity is 3 C per doubling. That is Myhre et al.'s 5.35 ln(ratio) W/m2 (3.7 W/m2 per
  doubling) at 0.81 C per W/m2, inside IPCC AR6's 2.5-4 C: **in range**. The CO2 term levels off at ±6 e-folds
  (CO2_MAX, tanh), which doesn't bind here (|co2| < 2 in these runs).
- **The frozen reference.** REF_FREEZE is 300 Myr (PW-558/559 B, PW-576). It sets where the thermostat steers, not
  how hard. v1-finish-6 showed that no physically argued variant of it warms anything.

Why it passes so much of a sustained forcing:
- The written steady-state gain is co2_sensitivity / ln 2 x WEATHER_K / WEATHER_CO2 = 0.97 C of CO2 cooling per C.
  That would pass ~half of a forcing.
- The realised gain is smaller, because the weathering doesn't see the global dT:
  - The latitude curve (`climate.compute`: equator +0.5 dT, pole +1.5 dT) warms the eroding low-latitude ground by
    only ~0.65 x dT (PW-576).
  - A warmer world uncovers cold high-latitude ground that weathers slowly.
- Measured:
  - within-run regressions (`slope.py`): d ln(temperature factor) / d dT is 0.025-0.030 per C, and the
    supply-weighted local temperature rises 0.12-0.24 C per C;
  - paired against base at 600-1000 Myr (C vs base, `gain.py`): the CO2 term answers -0.40 C per C, and **0.77 of
    the forcing reaches dT**;
  - PW-576's drift-instrumented gain: 0.047 per C, fb ~0.35 C/C.
- So the realised e-folding against the *global* temperature is ~21-38 K. That sits between the classic box-model
  10-20 K (Walker 1981, Berner's GEOCARB, which apply the kinetics to the global mean directly) and
  Krissansen-Totton & Catling's (2017) inversion of the last 100 Myr: 15-31 C of warming to double the weathering,
  Te ~22-45 K.
- The owner accepted ~0.35-0.5 C/C for PW-576 (2026-10-22). Nothing here is out of range, so per the brief it was
  not tuned.

To absorb a Sun-like star (~+13 C raw over the first Gyr) down to a +1-2 C trend, the realised gain would have to be
~4-5 C per C, a global e-folding of ~2-3 K. That is an order of magnitude past any literature value, so the
coordinator's "strong enough" thermostat doesn't exist inside the physics. **C′ as framed fails: 16/18 never-ice.**

The forcing's sensitivity was also corrected in the harness:
- v1-finish-6's `c_run.py` used 0.6 C per W/m2 (PW-564's estimate).
- The model's own value is co2_sensitivity / (5.35 ln 2) = 0.81. The model's 3 C is per *doubling*; the review
  note's 0.56 divided by 5.35 W/m2 as if it were per e-fold.
- A star as young as the planet on Gough's curve (+6.7% over 1 Gyr, ~0.65%/100 Myr) at 0.81 gives the same
  ~+13 C raw by 1 Gyr as v1-finish-6's 0.9%/100 Myr at 0.6.

## 2. The owner's lever: a slower star

The owner (2026-10-24) accepts the brightening rate as a planet parameter, chosen within the plausible range for
the star and reported as a not-quite-kludge.

The new parameters (`planet/tectonics/params.py`):
- `star_brightening` is the multiple of a Sun-like star's rate. It scales the star's evolution clock on Gough's
  curve.
- `star_age` is the star's age at the run's start. The default 0 means the planet is as young as its star.
- The forcing is counted against the run's start, so it is planet-relative (`earth.star_forcing`).

Plausibility of 0.45:
- Main-sequence evolution goes roughly as lifetime ~M^-2.5. 0.45 x the Sun's fractional rate is a star of
  ~0.73-0.75 solar masses: a mid-K dwarf, common, and a usual exoworld host.
- With that star the planet would orbit a bit closer to get Earth's insolation. The model's S0 / 4 (1 - 0.3) =
  238 W/m2 is unchanged.

The forcing:
- +1.6 C at 300 Myr, +3.3 at 600, +5.6 at 1 Gyr, +11.5 at 2 Gyr (raw, before the thermostat).
- 2 Gyr runs will be warmer late. That is untested here, and the draft below covers it.

The harness and the code differ slightly:
- The L6 sweep (`c7_run.py`, monkeypatched) scaled the forcing, RATE x (L(t) / L0 - 1).
- The code scales the evolution clock, L(age0 + rate x t) / L(age0) - 1. That is the physically cleaner form.
- They differ by < 3% of the forcing at 1 Gyr: 0.13 C at 0.45.

## L7 (the owner's main level): it holds

The code default (`star_brightening` 0.45) was run on the 4 showcase seeds, 1 Gyr, two draws (climate_offset 0 and
+0.001), through `tools/ice_diag.py` (`launch_l7.sh`). The bar and script are the same (`LEVEL=7`); per-seed lines
are in `passrate_L7.txt`.

| L7 | pass | icehouse median | early / late | always-icebox | never-ice | hellhole | dT median |
|---|---|---|---|---|---|---|---|
| base (v1-finish-5's l7fix_d1 + d2) | 3/8 | 45% | 36 / 37-62 | 0 | 0 | 0 | — |
| star 0.45, draw 1 | 4/4 | 29% | 0 / 34 | 0 | 0 | 0 | +3.7 |
| star 0.45, draw 2 | 3/4 | 24% | 18 / 38 | 0 | 0 | 0 | +3.6 |
| star 0.45, pooled | **7/8** | **25%** | 0 / 36 | 0 | 0 | 0 | +3.6 |

Icehouse % by seed (957317 / 619496 / 583167 / 639472):
- draw 1: 15 / 25 / 34 / 38;
- draw 2: 26 / 43 (F, by 3 points) / 19 / 23.

The max dT is +8.9..+13.0 (hellhole: median > 10.5 or any > 15.5). Deep ice is 0-22% of updates (583167 d1 22%,
under the 30% icebox line).

L7 keeps more of a late trend than L6 (late 34-38% against early 0-18%), but it is far from base's 57-62%.

## 3. Tests, scorecard, earth_check

(filled below)

## Files

- `c7_run.py` and `launch_c7.sh` run the L6 sweep (monkeypatched star; `LAM`, `RATE`).
- `launch_l7.sh` runs the L7 showcase seeds with the code default.
- `pr.sh` scores a sweep with v1-finish-6's `passrate.py`.
- `gain.py` gives the paired realised gain; `slope.py` the within-run regressions.
- `passrate_*.txt` hold the per-seed lines.
- Raw outputs are in the session scratchpad `v1f7/` (Cp, Cp06, R20, R30, R45, l7_d1, l7_d2).
