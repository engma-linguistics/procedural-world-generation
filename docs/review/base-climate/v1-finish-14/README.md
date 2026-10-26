# v1-finish-14: why 2 Gyr runs sit in icebox; PW-859 CH4/N2O; CO2's forcing log to 0.1 bar (2026-10-25)

Status: **measured; all three sets tallied (passrate_ghg_all.txt).** The code is b9eab15. The L6 2 Gyr set
is tallied. L7 1 Gyr (8 draws) and L6 1 Gyr (18 draws) are running under nohup.

## Cause (evidence: cpl_g2_sc0 seed957317, tools/ice_diag.py series)
- **The faint star.** A 2 Gyr run starts at -28.7 C of star forcing. It is still -25 at 300 Myr and -15.5 at
  1000 Myr.
- **The thermostat returns only ~40% of that before land plants arrive** (~470 Ma = run time ~1530). Bare ground:
  - weathers 1/PLANT_WEATHER of the planted reference, so the sink is x0.1-0.3 at X = 1;
  - goes as X^0.5, so ln X = 2 ln(s/w) - 2c dT, with c ~0.07/C (local kinetics at 0.5-0.6 of dT, plus runoff);
  - so the return is Gc/beta / (1 + Gc/beta), with G = 4.33 C per e-fold: ~0.38.
- That predicts dT ~-10 C at 300-1000 Myr. The run has dT -10..-12, a CO2 index of 3-4 and the sink at x0.1-0.25.
  This is not a sink or ice runaway: w_temp is ~1 and the albedo term is only -1.6 C. GEOCARB's own beta and
  kinetics give about the same return (~0.5), so this is a forcing budget, not a bug.
- **Smaller parts:**
  - The CO2 forcing's tanh level-off withheld 8% of the forcing at 20x and 18% at 150x, against its own docstring
    ("log up to ~0.1 bar").
  - No methane under low O2.
  - The outgassing drifts to ~0.7-0.8 of the spin-up's after ~750 Myr, worth ~-1..-3 C (draft-mantle-heat-by-age).
- **L7** is bimodal, not uniformly cold. On cpl: 3 of 6 draws iced; 2 others are hot at the end (+6, +10 C).

## Fix (b9eab15)
- **PW-859: CH4 and N2O as their own forcing** (earth.ghg_conc, ghg_forcing; the climate reads them, plants and
  weathering read CO2 only).
  - Each gas is a steady state of source x lifetime.
  - Sources: wetland CH4 at Q10 3 and soil N2O at Q10 2, on 0.7 dT of land temperature, the model's runoff, and the
    ice-free land.
  - LGM check: CH4 392 ppb, N2O 174 ppb (ice cores ~370 and ~200). The total is -0.5 C, about the literature's
    -0.5 W/m2 of non-CO2 GHG forcing.
  - Methane's lifetime goes with the oxygen calendar:
    - x43 between the GOE and the NOE: ~30 ppm, ~4 W/m2 (Pavlov 2003, Roberson 2011, Olson 2016);
    - x1400 before the GOE: ~1000 ppm, ~8 W/m2 (Pavlov 2000, Kasting 2005, Haqq-Misra 2008);
    - the steps are linear over 2400-2100 Ma and 800-540 Ma.
  - Forcings use Myhre 1998. CH4 goes over to ln above 5 ppm (Byrne & Goldblatt 2014), with the slope continuous.
  - The start balance includes it.
- **CO2 forcing:** exactly log up to ~0.1 bar (CO2_LOG = ln(1e5/350)), then levelling off over one decade
  (CO2_SAT, the maximum greenhouse near 1 bar). The cold side is unchanged.
- **Time zoom (PW-828):** this is already separate. The plants read CO2 through glacial_pco2 (0.68), and dTg carries
  all the gases. No change needed.
- pytest: 688 pass. The golden sim was updated on purpose. diag records `ghg` (C) and `ch4_ppb`.

## Measured: L6 2 Gyr, 13 draws (passrate_ghg_g2.txt)

| | cpl (1b52cdf) | ghg (b9eab15) |
|---|---|---|
| bar 300-end | 0/13 | 0/13 |
| bar 1000-1500 / 1500-2000 | 2/13, 4/13 | 2/13, 5/13 |
| median of draws' dT median | -5.4 | -3.7 |
| icehouse share | 87-100% | 81-99.8% |
| finish T -6..+3 | 5/13 | 6/13 |
| land ice 1-25% | 10/13 | 9/13 |
| trees >= 20% | 13/13 | 13/13 |

PW-859 plus the log fix warm the early 2 Gyr world by ~1.7 C (median), but every draw stays always-icebox. The
remaining gap is the bare-ground thermostat return (draft-faint-sun-thermostat-return-bare-ground, needs-decision).
Weathering has not been changed, as the coordinator asked.

## Running / resume
- `v1f14/all.sh` (nohup) runs `launch.sh g2` (done), then `l7`, then `l6`, with prefix `ghg`. It runs at most 3
  sims at once. The log is `scratchpad/v1f14/lane_ghg.log`, which ends `ALLDONE`; the outputs are
  `scratchpad/v1f12/ghg_*`. After a kill, rerun `nohup .../v1f14/all.sh &`. Finished draws are skipped.
- Tally: `bash docs/review/base-climate/v1-finish-12/pr.sh ghg` and `screen.py $V/ghg_*`.
- Not yet run on b9eab15: `tools/scorecard.py` and `tools/earth_check.py`. Run them after the set, keeping to 3 sims
  at once. earth_check should be nearly unchanged: GHG is 0 at dT 0 after the NOE.
- The 1 Gyr runs feel the Proterozoic methane at t < 460 Myr (1.0-0.54 Ga). In a smoke test, 619496 fix went from
  ICEB to a pass on the bar, with a warm finish (+5.9). Watch the L6 1 Gyr warm-finish count.

## Full set on b9eab15 (prefix ghg; passrate_ghg_all.txt)

| check | L6 1 Gyr cpl / ghg | L6 2 Gyr cpl / ghg | L7 1 Gyr cpl (6) / ghg (8) |
|---|---|---|---|
| bar 300-end | 16/18 / 16/18 | 0/13 / 0/13 | 3/6 / **7/8** |
| bar + finish checks | 9/18 / **12/18** | 0/13 / 0/13 | 0/6 / **4/8** |
| finish T -6..+3 | 12/18 / 14/18 | 5/13 / 6/13 | 3/6 / 5/8 |
| land ice 1-25% | 16/18 / 17/18 | 10/13 / 9/13 | 2/6 / 8/8 |
| trees >= 20% | 18/18 / 18/18 | 13/13 / 13/13 | 6/6 / 8/8 |

L7 and L6 1 Gyr reach the bar's ~70%, and L6 1 Gyr does not regress. 2 Gyr stays at 0/13 (see the
thermostat-return draft). earth_check on b9eab15: group 71.2%, exact 33.9%, log-rain corr 0.648, unchanged. The
scorecard line is committed.
