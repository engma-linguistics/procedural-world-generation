# Finish-temperature drift (lane 80, PW-1161 / PW-1158)

Data: lane 75's K judge (main physics after lane 75's ice merge), 18 L6 draws, roll 0.0005. No new runs. The scripts
here read `scratchpad/l75/judge/K_r0.0005_*` (the path `J` in an.py) and are run as `uv run python <script> K`.
Coordinator ruling: option C. Main is v1-acceptable, so no model change.

## Result
The drift is mostly physical variance of a sound loop. There are two systematic faults, but they offset.

- **Spread.** End T has median +0.1 C and sd 3.7 C. One forcing number, F = ln source - ln erosion supply (last
  10 Myr, against the frozen references, supply's reference at 250-300 Myr), gives R2 0.52 at 11.3 C per e-fold
  (lane 75's gain). F plus the albedo term gives R2 0.93. Albedo and CH4 amplify by ~1.4x. F has sd 0.24 e-folds.
  (reg.py)
- **Red, not jitter.** The ln source's cross-draw sd is 0.24 over the last 10 Myr, 0.20 over 50 and 0.17 over 100.
  Its autocorrelation is 0.95/0.89/0.71/0.49/0.10 at 2/4/10/20/50 Myr. The within-run sd about a 10 Myr running mean
  is 0.04. Plumes are 1.7% of the source. Cross-draw T sd grows from 1.8 C at 300 Myr to ~3.5 C after 550. (spec.py, ts.py)
- **No finish-window bias.** The window minus the 20 Myr before: ln src +0.025 +- 0.03, ln sink +0.01, T -0.04 C.
  The latest-habitable pick rescues only borderline draws (~1 C of spread in 10 Myr). (win.py)
- **Warm failures.**

  | draw | end T | ln src | ln supply |
  |---|---|---|---|
  | 639472 l6c_p | +7.3 | +0.02 | -0.33 |
  | 958504 l6c_p | +6.0 | +0.04 | -0.24 |
  | 639472 l6fix | +3.9 | +0.05 | -0.23 |
  | 583167 l6fix | +3.6 | +0.19 | -0.04 |

  For the first three, the erosion rate fell 0.27-0.45 e-folds while land area rose. The last one is a source
  case. (an.py, reg.py)
- **Cold failures.** 958504 l6c_0 (-5.0) is a source dip (-0.44). 819014 l6c_p (-4.6) is a lag: its source sat at
  -0.27 over 850-990 Myr and recovered only in the last ~10 Myr. Ice at 30% of land holds it cold, and its F is already +0.14.
- **Offsetting systematics.**
  1. Source decline: median ln src goes from +0.13 at 300-350 Myr to -0.13/-0.19/-0.14 over 850-1000. heat_start is
     1.0, so this is not mantle cooling (PW-1158). It is about -1.6 C.
  2. Supply step at the plants' arrival: the ln erosion rate drops by a median of -0.27 at the first planted step
     (16 of 18 draws negative, area flat, source control -0.05). It is -0.15 late. `erode()`'s
     `k_mult = 1 + 0.6 wet (1 - veg)` makes bare spin-up ground erode up to 1.6x faster. The sink reference counts
     the potential plants (`npp_pot`) but takes the bare supply. It is about +1.6 C. (plant.py)

  Fixing either alone moves the median ~1.5 C (inbox draft-sink-supply-reference-learnt-bare.md: fix both together, v2).
- **Bands (owner's call, no change).** A Gaussian at median 0 and sd 3.7 puts ~74% inside -6..+3 and ~21% above +3
  (observed 4/18). A warm edge near +4.7 C would leave ~10%. Earth's spread is larger (Phanerozoic GMST ~11-36 C,
  Judd et al. 2024). See draft-warm-finish-band-edge.md.
