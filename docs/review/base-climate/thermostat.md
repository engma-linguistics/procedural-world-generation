# The CO2 thermostat (base-climate lane B, stage 4)

Owner's decisions: PW-574 option A, as a smooth saturating weathering law (extra erosion counts for less and less
until it effectively stops; no hard cutoff). Option B (discount the cold era's erosion) rejected. Order after it:
PW-558 (CO2 as a stock), PW-559 (set point, option B), PW-564 (stellar brightening). Bars are judged on 10 L6 1 Gyr
seeds (1 2 5 7 11 13 21 42 99 3199) after the 300 Myr spin-up.

## Stage 0: measuring the gain (PW-572, second half)

**The sink's parts.** `earth.weathering(sim, land)` now returns the sink per cell and its parts. Both the run and the
diagnostics use it. With the old law the run stays bit-identical (the products are taken in the old order).
`tectonics/diag.Recorder` logs these every step, so that sink = supply × temperature factor × plant factor holds
exactly:
- `w_area`: the ice-free land's share of the surface;
- `w_supply`: the erosion supply from the bare ground (model units, like `sink_raw`);
- `w_plant`: the plant factor, weighted by supply;
- `w_temp`: the temperature factor, weighted by supply × plants;
- `w_T`, `w_q`: the supply-weighted local temperature and runoff;
- `w_rate`: the eroding land's mean erosion (km/Myr = mm/yr).

**The gain in `ice_diag --summary`.** Each file gets a `thermostat` line, computed by regression over the steps after
300 Myr:
- `fb`: the CO2 warming per C of cooling, co2_sensitivity × g / WEATHER_CO2, where g = d ln(sink)/dT with the land
  share held fixed. This is the review's `thermo2` measure, and the bar is 0.4–0.9.
- g raw, and d ln/dT of each part (supply, temperature factor, plant factor; area beside them). The parts add up to
  the raw slope.
- How much a C of dT moves the local temperature where the rock erodes.
- dT per C of drift.
- corr(CO2 term, dT), raw and with the volcanic source's part regressed out.

With more than one file, a closing line counts the seeds in the band and the seeds where the CO2 term runs against
dT.

Smoke test (seed 1, L4, 400 Myr, no ice): fb +0.54, almost all from the temperature factor (+0.068 per C).

**Measured on the drift, not on dT alone.** The first version regressed the sink on dT, as the review did. That
mixes two things:
- the gain;
- the thermostat's own answer to geography. Mountains on cold ground lower the sink, which raises CO2 and warms the
  planet. So by construction, a low sink goes with a warm planet.

The random drift knows nothing of the geography, so the summary now leads with the gain instrumented on it:
iv(y) = cov(y, drift) / cov(dT, drift). Each `thermostat` line gives:
- **CO2:** the CO2 term's answer, in C per C of cooling. This is what the climate actually gets, and the bar applies
  to it.
- **The sink's own answer**, d ln sink / dT, and its parts (supply, temperature factor, plant factor). Converted to
  fb with co2_sensitivity / WEATHER_CO2.
- **The same fb after the 10 Myr smoothing of the rates and the slow baselines** (`sink` relative to its ref).
- The regressions on a second line, for comparison with the review's numbers.

Caveat: 700 Myr of a drift with a 40 Myr memory is only ~17 independent samples, so one seed's iv is good to about
±0.1 C/C.

### Baseline on main (1252b40; 10 seeds, L6, 1 Gyr, after 300 Myr)

| seed | N1–N4 | icehouse % | CO2 answer, C/C | sink's own fb | after smoothing and baselines | supply /C | temp factor /C | regression fb | corr(CO2 term, dT) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | F | 78 | +0.01 | 0.31 | 0.18 | −0.000 | 0.038 | 0.34 | +0.20 |
| 2 | F | 84 | +0.02 | 0.28 | 0.22 | 0.018 | 0.023 | 0.23 | +0.47 |
| 5 | ok | 36 | +0.13 | 0.37 | 0.18 | 0.024 | 0.027 | 0.33 | +0.08 |
| 7 | ok | 38 | +0.19 | 0.35 | 0.13 | 0.032 | 0.024 | 0.38 | −0.18 |
| 11 | ok | 38 | +0.22 | 0.36 | 0.17 | 0.018 | 0.033 | −0.10 | +0.49 |
| 13 | F | 82 | −0.13 | 0.19 | 0.13 | 0.004 | 0.026 | 0.08 | +0.61 |
| 21 | ok | 39 | +0.11 | 0.27 | 0.25 | 0.004 | 0.037 | 0.22 | +0.42 |
| 42 | F | 82 | +0.45 | 0.41 | 0.33 | 0.023 | 0.042 | 0.15 | +0.26 |
| 99 | F | 61 | +0.51 | 0.74 | 0.50 | 0.049 | 0.055 | 0.34 | −0.01 |
| 3199 | F | 82 | +0.13 | 0.36 | 0.05 | 0.004 | 0.034 | 0.23 | +0.18 |
| **median** | 4/10 | 70 | **+0.13** | **0.35** | **0.18** | 0.018 | 0.033 | 0.23 | 2 of 10 negative |

**A controlled check** (`ctl.py` in the session scratch): the run's last climate call is re-made at dT − 4 on the same
ground and ice. Seeds 1 and 7, at 400 Myr:
- per C of dT, the eroding land's temperature moves 0.64–0.69 C (all land 0.8; land within 20° 0.51; globe 0.97);
- its rain moves 2.0–2.2% and its runoff 1.7–1.8%;
- the temperature factor moves 0.050 per C.

The eroding rock sits at |lat| 20–23° and 1.0–1.4 km up. There the climate's latitude curve moves the temperature
about 0.5–0.7 × dT, the equator 0.5 × dT (polar amplification).

### What this says (the cause, confirmed and corrected)
1. **Erosion doesn't swamp the temperature factor.** The supply rises with warmth (+0.00..+0.05 per C, median +0.018):
   a wetter world erodes more. The sea-level and incision route the review suspected isn't there: surface.erode's
   `base_rise` already takes the ice's sea-level fall out of the base level.
2. **The sink's own response is ~0.047 per C (fb ~0.35).** That's the temperature factor's ~0.033, which matches the
   controlled 0.05 less the noise, plus the supply's ~0.018. The design's 0.09 per C assumed the eroding ground warms
   1:1 with dT. It warms ~0.6:1, so even with perfect bookkeeping the per-cell rule gives ~0.4–0.5 C/C.
3. **The bookkeeping loses half of it, and the stage 0 tool finds this.**
   - The rates are smoothed over 10 Myr, which loses ~20%.
   - The baselines relearn over min(1000, 10 + t) Myr, 300–1000 Myr in the judged window. They take up a long cold
     era's deficit, which loses another ~30%.
   - So the sink, relative to its ref, answers at fb ~0.18. The volcanic source's chance correlation with the drift
     brings the CO2 term to a median of +0.13 C/C.
4. **The review's 0.14 C/C and "the CO2 term rises with dT on 12 of 15" are mostly the confound.**
   - The raw correlation is positive on 8 of 10 seeds, because the CO2 term follows the tectonic source and causes
     the warmth.
   - On the drift, the CO2 term pushes against dT on 9 of 10 seeds, just weakly.
   - The positive raw correlation is also what Earth's record shows: Phanerozoic CO2 and temperature go together.
     So a bar on the raw correlation would ask the thermostat to beat its own forcing.


## Stage 1: the weathering law (PW-574): attempt 1 fails, stopped for a decision

**The law tried.** The owner's option A, smooth saturation, in the spirit of West et al. 2005 and Maher & Chamberlain
2014. Per cell, W = c (1 − exp(−e / c)), where:
- e is the bare ground's erosion rate (mm/yr);
- c = C × runoff × exp(0.09 (T − 15)) × the plant factor is the kinetic ceiling, what the water running through the
  ground can take up;
- C = 1e-4 is the rock per water at the ceiling. That's a solute load of order 10–100 mg/L over a weathered fraction
  of ~0.3.

At low erosion, W ≈ e (supply-limited). At high erosion, W → c, and temperature and runoff steer. This C puts 40–57%
of the bare ground's erosion into the sink (probe on seed 1 L6). The kinetic share of the sink then answers c with an
elasticity of only 0.32–0.36.

**Result** (10 seeds, L6, 1 Gyr, the same code otherwise):

| | main | saturating, C 1e-4 |
|---|---|---|
| CO2 answer, median C/C | +0.13 | +0.14 |
| in 0.4–0.9 | 2/10 | 2/10 (seeds 5, 7; 13 overshoots at 1.09) |
| the sink's own fb, median | 0.35 | 0.35 |
| saturation term /C | | −0.017..−0.037 |
| CO2 term against drift-made dT | 9/10 | 8/10 |
| corr(CO2 term, dT) < 0 | 2/10 | 0/10 |
| N1–N4 pass | 4/10 | 2/10 (deep eras of 156–232 Myr on 5 seeds) |
| icehouse share, median | 70% | 76% |

**Why it can't work.**
- **Saturation takes the temperature out where it applies.** Ground that is supply-limited answers only to erosion,
  so the saturation term itself runs *against* warmth. The supply's answer to warmth (more rain, more erosion: +0.02
  per C) is what keeps the total level.
- **It fixes a cause the measurement doesn't find.** Stage 0 shows that erosion isn't swamping the temperature
  factor. The weak thermostat comes from two things:
  - the bookkeeping, the smoothing and the relearning baselines, which halves the sink's own answer;
  - the eroding ground warming at only ~0.6 × dT.
- **It weakens the brake on cold eras.** The tectonic sink's swings are damped, but the cold eras get longer.

More attempts at this law (a different C, or a Michaelis–Menten form) can't fix either cause, so I stopped after one
and wrote the decision up as a draft (`issue-tracking/inbox/draft-thermostat-cause-is-bookkeeping.md`). The code is
back to the old law. Stage 0's tools stay, and the run is bit-identical to main.


## Stage 2: CO2 as a stock (PW-558, PW-576 option C), lane B second agent

Owner's decision (PW-576 C): build CO2 as a stock, with a reference set once from the planet's own start balance
(PW-559 B). Judge "the CO2 term runs against dT" on the drift. Treat ~0.35-0.5 C/C as close enough.

**The code** (`planet/tectonics/earth.py`):
- `co2_stock`: dX/dt = (s − w X^0.4) / CO2_TAU, with X the stock (~pCO2) against the reference. Its steady state is
  the old ratio rule.
  - CO2_TAU = 0.4 Myr: the ocean-atmosphere carbon over the outgassing. The feedback's e-folding near the reference
    is ~1 Myr.
  - Backward-Euler substeps, solved by Newton's method in ln X. They are stable at any step length.
  - With no sink, X grows at s / CO2_TAU, without a ceiling.
- The 10 Myr smoothing of the rates is gone. The stock's own response replaces it. The CO2 index now jitters
  ~0.2 per step (was 0.05); dT's step-to-step sd goes 0.43 → 0.37-0.42 C.
- The forcing levels off smoothly (tanh) toward ±CO2_MAX = 6 e-folds. The old hard clip at 3 is gone.
- The references learn over 100 Myr until REF_FREEZE = 300 Myr, then are kept.
- `tools/ice_diag.py`:
  - the gain is also computed with each series' 200 Myr running mean taken out (`co2_hp`). A kept reference lets
    slow trends move the CO2 term, and over 700 Myr those trends line up with the drift's slowest wander by
    chance;
  - the band is now 0.35-0.9;
  - the summary prints the deep eras again: a stray `return` had hidden them.
- Tests: `tests/test_co2_stock.py`.

**Why the first-100-Myr reference the ticket proposed can't work.** The planet's own start isn't in balance:
- ln(source/sink) falls by 0.7-1.1 e-folds over the first 100-200 Myr on every seed;
- the erosion supply rises ~e-fold as the made-up start's low relief builds up (5 → 20-30 m/Myr);
- a reference from then would cool every planet by ~5 C.

So the balance is taken at the end of the spin-up.

### Results (10 seeds, L6, 1 Gyr, judged after 300 Myr; main = 2684f2b with lane A's stages merged)

| | main | att. 1: kept at 300 Myr | att. 2: kept once erosion settles | att. 3: att. 1 + relief term |
|---|---|---|---|---|
| CO2 answer, trends out, median C/C | +0.22 | **+0.44** | +0.32 | +0.28 |
| in 0.35-0.9 | 2/10 | **7/10** | 4/10 | 3/10 |
| CO2 term against drift-made dT | 8/10 | **10/10** | 10/10 | 10/10 |
| N1-N4 pass | 5/10 | 5/10 | 5/10 | **8/10** |
| icehouse share, median (in 15-45%) | 58% (3) | 66% (1) | 58% (2) | **35% (5)** |
| mean dT after 300 Myr, median | −1.4 | −0.9 | −0.9 | +0.9 |
| fails | deep eras 192-276 Myr (2, 13, 99, 3199); share | deep eras 156-340 Myr (2, 5, 11); share (13, 3199) | share 77-93% (1, 13, 99); 5% (21); icehouse 316 Myr (2) | icehouse 304 Myr (42); share 2% (7) |

**Attempt 1** (references kept from 300 Myr):
- The thermostat reaches the bar: 7/10 in band, median +0.44, and on every seed the CO2 term runs against the
  drift-made dT.
- But the deep eras on seeds 5, 7 and 13 have the sink 1.4-1.8× above its reference. CO2 is *drawn down* inside
  the cold era (index −1.2..−1.6). The erosion supply keeps rising after 300 Myr, by +0.3-0.6 e-folds by 1 Gyr: the
  relief is still building. A kept reference turns that into a lasting cooling.
- Two 2 Gyr runs (seeds 5 and 13) show the supply levelling off only at ~500-700 Myr, then creeping on.

**Attempt 2** (references learnt until the ice-free land's erosion rate grows by less than 10% per 100 Myr):
- The references were kept only at 376-846 Myr. For most of the judged window they were still learning over
  100 Myr, so the brake weakened again (median +0.32).
- The deep eras did end (N1 fails on one seed only, by 14 Myr). The failures moved to the icehouse share (N3).

**Attempt 3** (attempt 1, plus a relief term):
- The ice-free land's erosion rate is measured against its own 200 Myr mean (`RELIEF_MYR`).
- The ice-free share, the temperature factor and the plants stay measured against the kept balance.
- So the cold era's deficit from ice and cold is kept, while the relief's slow build-up doesn't drift the climate.
- The cost: the runoff part of the brake (~0.018 per C of 0.05-0.08) is partly forgotten over long eras.
- **Result:**
  - N1-N4 pass on 8/10, the multi-seed bar. Every deep era ends; the longest is 128 Myr (seed 42).
  - The icehouse share's median is 35%, with 5/10 seeds in 15-45%. Seeds 7, 21 and 5 are too warm (2%, 8%, 14%);
    seed 42 has an icehouse of 304 Myr.
  - The CO2 answer is +0.28 C/C median with the trends out (+0.30 with them), 3/10 in 0.35-0.9. It runs against
    drift-made dT on 10/10 seeds.
- The thermostat lands a little under the owner's "close enough" (0.35). Its spread is ±0.1 per seed from 17
  independent drift samples, and per seed the sink's own fb is 0.0-1.2 (median 0.41).
- The planets now run warm. The mean dT after 300 Myr is +0.9, and the CO2 index rises late on 7/10 seeds: the source
  creeps up (+0.3-0.5 e-folds over 2 Gyr), and the relief term forgets part of the sink's rise.
- So the set point (PW-559) may only need to be small, or none, on this stock. Judge that on its own sweep.
- Results: `laneB2/stock3/` in the session scratch.

**What remains.** Attempts 1-2 left the median icehouse share at 58-66%; attempt 3's relief term brings it to 35%. The stock fixes the brake; it can't move the planet's mean state, because dT = 0 is
today's icehouse Earth. The relief spin-up is a surface/setup issue (inbox draft `draft-relief-spinup-erosion-rise`).
