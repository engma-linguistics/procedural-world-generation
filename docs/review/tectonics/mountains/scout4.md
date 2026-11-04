# PW-1446 scout 193: why the height cap widened the late-climate spread (pass 2 of 3, diagnosis only)

Scout 193, 2026-11-04, on main 19bd39a5. No new runs and no model changes. The data are scout 190's judge outputs
(`tools/ice_diag.py` records of both arms; `main` = lane 181's `kn` arm, `cap` = held/scout190-max-km 59d774f3), plus
the 8-draw screen, where both arms record the hypsometry. Scripts beside this file:

- `scout4_table.py` gives one row per draw: late-window (600-1000 Myr) means of the carbon cycle's parts, slopes against
  dT within each run, and the hypsometry.
- `scout4_spread.py` gives per-arm spreads, correlations with dT, and the paired changes.
- `scout4_decomp.py` splits the carbon imbalance's variance exactly across draws, with a paired bootstrap.
- `scout4_gain.py` runs `ice_diag.gain` (the thermostat's gain, instrumented on the drift) on both arms, paired.
- `scout4_coupling.py` gives the outgassing–erosion coupling by sub-window, the spread per 133 Myr window, and a
  permutation test.
- `scout4_persist.py` gives autocorrelation within runs and how window means correlate across draws.

## In plain words

- **The hypothesis is wrong for this model, and it is wrong by construction.** The weathering sink is a product:
  erosion supply × a climate factor × a plant factor (`earth.weathering`). So how hard weathering answers a warmer
  climate (d ln sink / dT) does not depend on how much the mountains erode. Lower mountains can change how much the
  planet weathers. They cannot make the thermostat weaker. The data agree:
  - the CO2 rise per unit of imbalance is the same (4.48 vs 4.67 e-folds per e-fold);
  - the ice-albedo gain is the same (0.25 vs 0.25 C per C);
  - the weathering's temperature damping is the same within noise (−0.0011 vs −0.0014 of the imbalance variance);
  - per run, the regression d ln sink / dT is the same (median −0.017 vs −0.023 per C).
- **The mountains' share of weathering did not shrink either.** Across the 36 draws, the mean ln(erosion supply) is
  5.096 on main and 5.093 on the cap, and its spread between planets is 0.066 and 0.062. Land above 3 km fell a lot on
  some draws. On 619496 it went from 7.9% to 1.0% and the supply fell only 14%. Supply is set by uplift, not height.
- **High land does act on the climate, but as a push, not a brake.** More high land means more erosion supply
  (r +0.8 in both arms), more weathering, and a colder planet. On the cap arm, r(land > 3 km, late dT) is −0.65, about
  −0.6 C per point of land above 3 km. The draws that lost the most high land went warmer (619496, 639472 and 819014
  went from −0.6 / −0.4 / +0.6 C to +2.4 / +2.6 / +3.7 C). The one that gained high land went colder. This shifts where
  each draw sits. It does not, by itself, widen the set.
- **What actually widened is how long each planet stays off-centre, not how far off it gets.** In each 133 Myr window
  of the late period the spread between planets is 2-3 C on both arms, and the cap is not wider:
  - 600-733 Myr: main 2.67 vs cap 1.97;
  - 733-866 Myr: 2.52 vs 2.63;
  - 866-1000 Myr: 2.32 vs 2.89;
  - none of these is significant.

  The judged number averages over 400 Myr. On main, a planet that is warm in one window tends to swing back, so the
  windows correlate +0.02, −0.07 and −0.30 across draws and the average narrows to 1.25 C. On the cap a warm planet
  tends to stay warm (+0.28, +0.38, +0.03), so the average keeps more of its spread (1.80 C). A paired permutation test
  gives p = 0.015 for the 400 Myr sd. Within each run nothing differs: dT's within-run sd is 3.29 vs 2.98, and its
  autocorrelation at 10-100 Myr matches.
- **Which planets end up in the tails** is decided by outgassing chaos. The cap re-rolls each planet's tectonics: the
  paired change in ln outgassing has sd 0.12, more than the 0.08 spread between planets in either arm. A draw's change
  in late dT follows its change in ln(outgassing / erosion supply) with r = 0.84. The cold tail is planets whose
  outgassing fell while their erosion supply did not. The two coldest cap draws (958504 `l6c_m` r0.0005 and 957317
  `l6c_p` r0.001) also hold the most high land (8% and 11% above 3 km).
- **One lead did not hold up.** Across all 36 draws, outgassing and erosion supply correlate +0.41 on main and +0.04 on
  the cap. That looked like a decoupling: on main, active planets build more mountains and so weather more, which cancels
  part of their extra CO2. But the correlation changes sign from window to window in both arms (main 0.10 / 0.05 /
  0.59; cap 0.41 / 0.45 / −0.02). It is sampling noise, not a property of the cap.
- **Verdict.** The relief/erosion term does not lose strength, and the thermostat does not damp less. The 1.25 → 1.80
  widening is a real difference in the 400 Myr average (p ≈ 0.015). Its whole cause is that per-planet offsets persist
  longer across windows on the cap arm. On 36 draws that is about a 2σ effect, and no thermostat part I could measure
  explains it. Main's 1.25 is itself below the bar's 1.3-1.7. Taking both arms' variances together gives 1.55, which is
  inside the bar. The likeliest reading is that the cap moves where each planet sits (through high land and re-rolled
  outgassing) and the 36-draw sd of a 400 Myr mean is noisier than the bar assumes. I have not shown that. Pass 3 should
  re-measure before any mechanism is changed to chase the number (candidate 0).

## 1. How the code makes the climate (what can and cannot widen the spread)

`earth.global_temperature` holds CO2 in balance every step. `CO2_TAU` is 0.4 Myr, far below a step. The balance is
`sink_raw · co2_law(X) = source_raw · exp(−YARDSTICK)`, with:

- `sink_raw = w_supply · w_plant · w_temp`: the erosion supply from ice-free land (`sim.weathered`) × the plant factor
  × the climate factor, which is `exp(WEATHER_K (T − 15)) (q / RUNOFF_REF)^0.65` weighted by supply and plants;
- `source_raw`: ridges + 20 × arc growth + plume CO2, times the drift factor;
- `YARDSTICK[6]` = 1.377: fixed once `REF_FREEZE` (300 Myr) has passed.

So ln co2_law(X) = ln source − ln supply − ln plant − ln temp − 1.377 holds exactly. The diag records carry every part:
`source_raw`, `sink_raw`, `w_supply`, `w_plant`, `w_temp`, `w_T`, `w_q`, `w_rate`, `w_area`, `w_a` (the CO2 log-slope),
`co2`, `co2_term`, `albedo_term`, `ghg` and `drift`.

Two consequences follow:

1. The relief factor (`w_supply`) is a multiplier. It moves the balance's level, and with a fixed yardstick that
   level shift becomes the planet's climate. It cannot change d ln sink / dT. That slope is set by `WEATHER_K`, the
   runoff exponent and the local temperature's response, all the same on every cell whatever its erosion rate.
2. The spread between planets equals (the spread of the tectonic imbalance ln(source / supply / plant)) × (the loop's
   gain). The gain is set by `co2_law`'s slope, `co2_sensitivity`, the ice albedo and the climate factor's response.
   A change in spread must come through one of these two.

## 2. The gain is unchanged (`scout4_decomp.py`, `scout4_gain.py`)

Across the 36 draws, late window. "Imbalance" is ln(source / sink). The CI is a 95% paired bootstrap.

| | main | cap | cap − main [CI] |
|---|---|---|---|
| sd late dT | 1.250 | 1.804 | +0.55 [+0.11, +0.96] |
| sd imbalance | 0.042 | 0.058 | +0.017 [+0.002, +0.030] |
| CO2 per unit imbalance (e-folds) | 4.48 | 4.67 | +0.19 [−0.23, +0.63] |
| ice-albedo C per C of dT | 0.246 | 0.253 | +0.007 [−0.05, +0.07] |
| d ln w_temp / d dT across draws | 0.0213 | 0.0129 | −0.008 [−0.024, +0.004] |
| imbalance variance from the source | 0.0024 | 0.0032 | +0.0009 [−0.0010, +0.0027] |
| from the supply | 0.0004 | 0.0017 | +0.0013 [−0.0007, +0.0031] |
| from the climate factor (the damping) | −0.0011 | −0.0014 | −0.0003 [−0.0015, +0.0009] |
| r(ln source, ln supply) | +0.41 | +0.04 | −0.36 [−0.80, +0.04] |

Per run (`ice_diag.gain`), median main vs cap:

- OLS d ln sink / dT with land fixed: −0.017 vs −0.023;
- the drift-instrumented CO2 answer: −1.06 vs −1.00 C per C;
- dT per unit of drift: 0.71 vs 0.69.

The instrumented values scatter widely from draw to draw (the drift is a weak instrument at this size of effect), and
none of the paired means moved. dT's sd per unit of imbalance sd is 29.8 on main and 30.9 on the cap: the same loop.

Alternatives checked:

- Land share: same mean and sd (0.344 / 0.345, sd 0.006 both).
- Albedo of ice and high land: same gain per C. Its larger sd (0.37 → 0.53) is the larger dT spread passed on.
- Rain over mountains: runoff on the eroding land `w_q` has the same mean (946 vs 949 mm). Its sd between draws grew
  (54 → 72), but `w_temp`, which carries it, has the same spread.
- Plants: `w_plant` sd 0.012 vs 0.013.

## 3. The relief share does not shrink, and does not track the tails (`scout4_spread.py`, screen hypsometry)

- Across the 36 draws, mean ln `w_supply` is 5.096 vs 5.093, and its sd is 0.066 vs 0.062. Erosion per eroding cell
  `w_rate` is 0.026 vs 0.026 mm/yr.
- On the 8-draw screen, both arms record `hyps`. Land above 2 / 3 / 4 km has r +0.84 / +0.78 / +0.76 with ln supply on
  main, and +0.84 / +0.81 / +0.82 on the cap. High land is where the supply comes from. Yet 619496 (l6fix r0.0005) lost
  land above 3 km from 7.87% to 1.01% and its supply fell only 0.15 in ln. 639472 went from 6.23% to 0.91% and its
  supply fell 0.06.
- Paired change in land above 3 km vs paired change in late dT, on the 8 screen draws: r −0.47, about −0.4 C per point.
  Losing high land warms a draw, as PW-451 expects. On the cap arm across 36 draws, r(land > 3 km, late dT) = −0.65.
- Does the widening track the loss of high land? No. On the screen, the paired change in |dT − 1.5| *rises* with the
  change in high land (r +0.78): the draws that lost the most high land moved from the cold side toward the warm side.
  Across the 36 draws, the change in |dev| correlates −0.45 with the change in ln `w_temp` and +0.39 with the change in
  ln supply. A draw that went to a tail did so through its imbalance, not through a weaker brake.

## 4. Where the widening is: persistence across windows (`scout4_coupling.py`, `scout4_persist.py`)

| window (Myr) | sd dT main / cap | sd imbalance main / cap | sd ratio, permutation p |
|---|---|---|---|
| 300-600 | 0.90 / 0.82 | 0.089 / 0.087 | 0.91, 0.56 |
| 600-733 | 2.67 / 1.97 | 0.114 / 0.087 | 0.74, 0.13 |
| 733-866 | 2.52 / 2.63 | 0.078 / 0.091 | 1.05, 0.78 |
| 866-1000 | 2.32 / 2.89 | 0.078 / 0.093 | 1.25, 0.13 |
| **600-1000 (judged)** | **1.25 / 1.80** | 0.042 / 0.058 | **1.44, 0.015** |

How the window means of dT correlate across draws:

| | w1-w2 | w2-w3 | w1-w3 |
|---|---|---|---|
| main | +0.02 | −0.07 | −0.30 |
| cap | +0.28 | +0.38 | +0.03 |

These reproduce the judged sds exactly: var(mean) = Σ var / 9 + (2/9) Σ cov, giving 1.27 and 1.77. Within runs, the
two arms have the same autocorrelation of dT, CO2, source, supply and imbalance at 10/25/50/100 Myr. dT at 200 Myr is
−0.38 vs −0.27, and the drift, identical in both arms, is −0.40 at that lag. Main's late climate swings back on a
~200 Myr scale slightly more than the cap's.

The late dT of the two arms correlates −0.39 draw by draw. Chaos re-rolls each planet completely, so the comparison
is between two independent samples of 36.

Main code's late-dT sd has been measured once on 36 draws: 1.25, and 1.26 for round3's C1, a near-identical arm. The
bar "about 1.3-1.7" was set when the arm read 1.73 (D47). A 36-draw sd has about 12% sampling noise (1σ ≈ 0.18 at
1.5). On top of that comes the window-persistence effect above, which a different set of draws can flip.

## 5. Candidates for pass 3

**0 (do this first; measurement, not a mechanism): re-judge both arms on new rolls.**

- What it changes: nothing in the model. It adds a second, independent 36-draw set for main and cap, ideally with
  lane 144's forked paired judge (`paired_fork.sh`), which starts both arms from a shared checkpoint. Lane 144 found it narrows the late-dT
  spread by about 19%, so a forked re-judge should be compared with a forked main, not with the 1.3-1.7 band as is.
- Why: every part of the loop that I can measure is unchanged. The judged difference sits entirely in how window means
  correlate across 36 chaotic draws, a ~2σ effect. If the cap still reads above 1.7 against main's spread on a second
  set, there is something to explain. If not, the cap passes as is.
- It does not loosen the bar: the same bar is applied to more evidence.

**1: conserve the crust the height cap removes (lateral spreading, not deletion).**

- What it changes: `crust.flow_and_orogeny` and `Simulation._write_back` delete the crust above `isostasy.max_km`
  (booked as `flow+cap` / `clip`). Instead, the excess would join the existing thickness flow (`crust_flow`) toward
  lower neighbours. That flow would be driven by the column's height, not only its thickness, so a plateau at its limit
  widens rather than losing mass.
- Why it is physics: a plateau at its height limit spreads its crust sideways through lower-crustal flow. Clark &
  Royden 2000 (Geology 28: 703-706; abstract fragments and citing summaries only) model the eastern margin of Tibet as
  crust flowing out under the plateau's topographic gradient. scout3.md §1 cites Dewey 1988 and England & Houseman 1989
  for the collapse; I did not re-read those. Deleting the crust is bookkeeping: the mass should go somewhere and erode
  there. That keeps an active planet's arc and collision crust turning into erodible land, which keeps outgassing and
  weathering tied through plate activity.
- Honest status: it is a soundness fix for scout 190's change. My data do not show that the cap's deletion decouples
  outgassing from supply (the §2 correlation is noise), so I can make no claim about the spread. Pass 3 should first
  read how much `flow+cap` + `clip` deletes per Myr on both arms (`sim.book`; not in the diag records), from a short L6
  run of each.

**2 (flag only; would likely widen, not narrow): erosion-dependent weathering regimes.**

- What it changes: the climate factor's temperature sensitivity would scale with how fast a cell erodes. Slow-eroding
  cells are supply-limited: the sink follows erosion, with little T-sensitivity. Fast-eroding cells are kinetically
  limited, with the full `WEATHER_K` and runoff law.
- Why it is physics: West, Galy & Bickle 2005 (EPSL 235: 211-228; read: the abstract, §4 Discussion p. 223-225, and
  Fig. 3) find that "At lower erosion rates mineral supply limits weathering. At higher erosion rates there is abundant
  material but kinetic and therefore climatic factors limit weathering" (abstract). They also find that "the feedback
  process which moderates global climate on long time scales takes place in more rapidly eroding terrains" (p. 223).
  In this regime law, the brief's hypothesis would be true. Lower mountains *would* weaken the thermostat.
- Why it is not a pass-3 fix for this bar: the model today gives every cell kinetic sensitivity, which makes the
  thermostat stronger than this physics allows on low-relief planets. Adding it would widen the spread. It is a
  soundness gap (inbox draft), not a remedy.

## 6. What was not done

- No runs, no tuning, no code changes.
- Main's 28 non-screen draws have no hypsometry, so §3's paired high-land analysis is the 8-draw screen only.
- The cap's deleted mass is not in the diag records (candidate 1's first step).
