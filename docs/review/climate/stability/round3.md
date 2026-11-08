# Climate stability, round 3 (lane 170, 2026-11-03): building D47 option C

D47 option C, approved by Daniel on 11-03: PW-1424 A + C (one carbon-cycle yardstick per grid level; the weathering
reads plant cover) and PW-1425 (frozen over = ends or stays frozen). Rounds 1 and 2 (lanes 158, 160) are the
diagnosis and the check of A alone. Baselines: "main" is current main 1ecdad3a, run here on the judge's own 36 draws.
Lane 140's main runs (4abc1707) are not current main: lane 142's moc_lambda change (PW-1381) came after them.
"Today's Earth" is the climate model's dT = 0.

## Diagnosis written before any run

### A. One yardstick per grid level
- **What changes.** Today each planet learns two references in its first 300 Myr: its volcanic source and its
  weathering sink at the balance climate. Then it keeps both. y = ln(source ref / sink ref) is a sample, and rounds
  1-2 measured it as a dice roll (sd 0.16 between re-runs of one planet). After the change the source reference is
  still learnt. It is the planet's own outgassing and sets the units. The sink reference is set to
  source ref x exp(-Y_level) from the first step after REF_FREEZE. Y_level is one constant per grid level. The learnt
  sink reference stays in the state as a diagnostic: `tools/yardstick.py` reads the learnt y from any run's 300-Myr
  record and gives the mean that Y should be re-fit to.
- **Planet-relative.** Y is a ratio. A planet that outgasses twice as much gets a sink reference twice as large, so
  nothing is in Earth units.
- **Expected effect** (round 2, measured with lane 160's runs): the spread of the late climate across all 36 draws
  narrows from 2.6 C to about 1.7-1.9 C. The cold tail (yardsticks that drew high) and the warm tail (drew low) both
  pull in. The centre stays where it is, within the twins' chaos. Re-runs of one planet still disagree by about
  1.4-1.8 C (plate chaos). No draw is pushed hot.
- **L6 value.** Y_6 = the mean learnt y of this arm's own 36 spins, which include C. Lane 158 measured 1.316 on
  main 4abc1707 without C.
- **L7 value.** No L7 judge set exists. The run store has six L7 runs with the stock settings and
  star_brightening 1.0 (gallery-stock-1..4, 10-27; v010-earthlike-a/b, 11-01). Their learnt y is 1.308, 1.599, 1.282,
  1.680, 1.530 and 1.652: mean **1.508**, sd 0.17. These are older code, before C. Y_7 = 1.508 + (Y_6 with C - the
  same draws' y without C). That assumes C shifts y by the same amount at L6 and L7. A draft asks for an L7 check.
- **Other levels** take the nearest measured level (L3-L6 take Y_6, L8 takes Y_7). Runs that stop before 300 Myr
  never reach the pin.

### C. Weathering reads rooted plant cover, not NPP
- **What changes.** `plant_factor` was 1 + (PLANT_WEATHER - 1) x min(NPP / 500 g C/m2/yr, 1). Now it is
  1 + (PLANT_WEATHER - 1) x the cell's rooted cover. Rooted cover is the summed cover of trees, shrubs and herbs. It
  leaves out the moss and crust "ground" types, since GEOCARB's f_E is about vascular plants being there. Cover is
  taken from the plants grown at the balance's CO2 (as npp_w was, PW-880), so the air's CO2 still reaches the sink
  only through FERT. The reference is built the same way, from the spin-up's potential vegetation. NPP_WEATHER goes.
- **Forecast, on the 36 main 300-Myr states** (`cov.py` in the scratchpad; supply-weighted, as the sink weighs it):
  the reference plant factor rises by 2.6% on average (sd 2.0%). At the weathering ground the cover factor is
  2.55-2.76 and the NPP factor 2.42-2.71. Most rock weathers where plants already sat near NPP_WEATHER. So C shifts
  the learnt y by about -0.026, and Y_6 should come out near 1.29. Grass and tundra get their full factor, which
  gives the largest rises (+5-7%). Those are on the cold draws (y 1.42-1.79), so C alone would warm main's cold
  tail a little. Under A that is absorbed into Y.
- **Expected effect on the climate.** After Y is re-fit, the centre should be unchanged within about 0.3 C. The
  plant term was 21% of the twins' carbon-balance difference (round 1, section 2). Cover saturates, so that term
  shrinks and the twins split a little less. It may also be slightly weaker as a thermostat, because warmer
  climates no longer add weathering through more NPP, though cover still follows the climate. What it is for: a
  plant-growth fix (PW-1332, PW-1261) no longer moves the climate by 3-5 C.

### PW-1425. Frozen over means ends or stays frozen
- **Old rule:** fail if land ice is >= 40% at any climate update in the hard window (884-1000 Myr on these draws).
- **New rule (approved):** fail if the world ends frozen: land ice >= 40% at the run's last climate update, and no
  finish-window candidate passes the finish moment's land-ice check (1-25%). A world that has stayed at >= 40% from
  some time to the end also ends at >= 40%, so it fails the same way. The 40% line is unchanged. The hard window's
  peak stays as a reported measure (`frozen_peak`), together with the time at >= 40% and the length of the last
  frozen spell.
- **Expected effect:** on lane 160's pinned runs, 1 of 72 fails the old rule and 0 of 72 the new one. On lane 158's
  five histories of one cold planet, 2 of 5 fail the old rule and 0 of 5 the new one.

### The judge
One candidate and no sweeps. Main (1ecdad3a) runs `paired.sh` on the 36 draws. The candidate is spun to 300 Myr
with `fork.py spin` (its own code), Y_6 is read from the spins, and the candidate continues from the spins with
`fork.py cont`. The pin starts after 300 Myr, so each continuation is the same run as a straight run of the final code.
Pass bar: 0 hard failures under the new rule, a soft pass count within chance of main (McNemar), and late dT inside
-6..+5 C of today's Earth. Expect 1.4-1.8 C of re-run chaos per draw (round 2), so read the paired medians.

## Results (lane 170b, 11-04 04:45)
Both arms ran on the same 36 draws (2 rolls x 18). "main" = 1ecdad3a straight (`paired.sh`); "cand" = this code with
Y_6 1.377 (`fork.py spin` to 300 Myr, then `fork.py cont`). Late dT = mean dT over 600-1000 Myr; dT 0 is today's
Earth in the model. Read-outs in the scratchpad: `ana.py` (per draw), `tails.py`, `tools/judge.py paired`,
`tools/hard_bar.py` on symlink roots `hb_main/`, `hb_cand/`.

### The bar: passes
| check | main | cand |
|---|---|---|
| hard: frozen over at the end (PW-1425) | 0/36 | **0/36** |
| (old rule, 40%+ at some moment of 884-1000, reported) | 0/36 | 0/36 |
| hard: boiled / hellhouse | 0/36 | 0/36 |
| hard: ocean loss | 0/36 | 0/36 |
| hard: CO2 crash (below the plants' compensation point) | 0/36 | 0/36 |
| soft pass (bar + finish moment) | 28/36 | **30/36** |
| late dT outside -6..+5 C of today's Earth | 2/36 (+5.35, +6.44) | **0/36** |
| peak land ice in 884-1000, mean / max | 15.4 / 39.7% | 15.0 / 33.5% |

McNemar on the soft pass: both 22, main only 6, cand only 8, exact p 0.79: within chance of main.
Secondary, reported: CO2 under 100 ppm 1/36 main, 2/36 cand; 8-fold fall in <= 50 Myr 24/36 main, 21/36 cand;
end pCO2 outside 180-600 ppm 19/36 main, 13/36 cand.

### The centre: unchanged within the chaos
Paired cand - main over the 36 draws (judge medians, 95% CI): late dT +0.36 C [-0.55, +1.09], end T -0.96 C
[-1.75, +1.55], late CO2 +0.00 e-folds, trees +1.4 points, arid -0.7 points. None moved (sign p >= 0.13). Mean late
dT +1.10 C main, +1.40 C cand (mean paired difference +0.30, sd 2.68: the 1.4-1.8 C re-run chaos per arm, twice).

### The spread across planets: narrower, as forecast
| late dT over the 36 draws | main | cand |
|---|---|---|
| sd between draws | 2.09 C | **1.73 C** (forecast 1.7-1.9) |
| range | -2.60..+6.44 | -3.39..+4.80 |
| 10th / 25th / 50th / 75th / 90th percentile | -1.55 / -0.46 / +0.95 / +2.56 / +3.23 | -0.69 / +0.44 / +1.28 / +2.77 / +3.26 |
| interquartile range | 3.02 C | 2.34 C |
| mean distance from the median | 1.66 C | 1.33 C |
| within-seed sd (re-runs of one planet) | 1.89 C | 1.68 C |
| draws colder than -1 C / warmer than +3 C | 8 / 5 | 4 / 7 |
| hottest / coldest single late step | +12.0 / -10.4 | +11.8 / -9.3 |

- **Cold tail pulls in** most: the 10th percentile goes from -1.55 to -0.69 C, half as many draws below -1 C. One cand
  draw is colder than any of main's (r0.001 l6c_m 53669, -3.39 C against main's -2.04 on the same draw; its learnt y
  1.458 was not the cause, since the pin replaces it, so this is that planet's plates).
- **Warm tail**: main's two hot outliers (+5.35, +6.44, both draws whose learnt y drew low, 1.08-1.09) come in to
  +0.46 and +0.97. The 90th percentile is unchanged (+3.2 C), and more draws sit at +3..+5 (7 against 5): the
  warm side is shorter, not thinner.
- Main's 9 coldest draws average -1.53 C on main and +0.64 C on cand; its 9 warmest +3.67 and +1.15. Part of that
  is regression to the mean (picked on main's own chaos), so read the sd and percentile rows above as the measure.

### The yardsticks
- **Y_6 = 1.377** (cand's 36 spins, sd 0.207; unchanged).
- Main 1ecdad3a's learnt y on the same draws: mean 1.343 (sd 0.175). C's shift = cand - main = **+0.034** (paired sd
  0.197, standard error 0.033). The forecast was -0.026 from the 300-Myr states (`cov.py`); the measured shift is
  within about one standard error of zero and of the forecast, so C does not move the yardstick measurably.
- **Y_7 = 1.508 + 0.034 = 1.542** (set). It rests on the six older L7 store runs (sd 0.17, standard error 0.07),
  so it is the least certain number here; the inbox draft asks for an L7 measurement.

### Verdict
C + A pass the bar: 0 hard failures under the ends-frozen rule, soft pass 30/36 against main's 28/36 (p 0.79),
every draw's late dT inside -6..+5 C of today's Earth. The spread between planets narrows from 2.09 to 1.73 C sd,
mostly by pulling in main's cold tail and its two hot outliers; the centre does not move beyond chaos.

### Tests, Earth check, scorecard (commit ca715232)
- `pytest -n 4 -m "not slow"` (golden deselected): 979 passed, 1 skipped. Climate-area slow tests (`test_envelopes.py`,
  `test_sea_level.py`): 16 passed, 1 skipped. `test_golden.py --update-golden`: `sim_L4_s1_60myr.json` rewritten
  (C moves it; A starts after 300 Myr), then 2 passed without the flag.
- `tools/earth_check.py` (L6): Koppen main group 71%, exact code 37%, log-rain correlation 0.718, global mean T 13.9 C
  against NCEP's 14.0. The same as main's last scorecard line (ceabe3ae: 71.4 / 37.5 / 0.718), as expected: the Earth
  check runs the climate at dT 0 and never reaches the carbon cycle.
- `tools/scorecard.py`: line appended for ca715232. Seed 1 at 1000 Myr: ice 5.8%, trees 31.8%, NPP 390; seed 2: ice
  1.7%, trees 53.5%, NPP 546 (ceabe3ae: 0.5 / 41.4 / 427 and 6.6 / 32.4 / 331). Single seeds, inside the re-run chaos.
- Scratch kept: `l170/judge/` (both arms' 72 runs), `ana.py`, `tails.py`, `yard_spins.txt`, logs. Spins and code copies
  removed.
