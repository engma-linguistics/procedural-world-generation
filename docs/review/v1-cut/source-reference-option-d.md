# Option D for PW-1645 / PW-1158: learn the CO2 source's reference later (lane 273): diagnosis

## In plain words

Option D cannot fix the late cold tail, because the climate no longer reads the source's reference. Since PW-1424 A,
the weathering's reference after 300 Myr is the source's reference over one fixed constant (YARDSTICK). So the
reference appears on both sides of the CO2 balance and cancels. The CO2 level a run settles at depends only on the
planet's actual outgassing against its actual weathering. A later or longer reference relabels the diag's "source
against its reference" (819014's 0.68-0.69 would read 0.78-0.86), but the temperature does not move. Learning both
references later and re-fitting YARDSTICK moves every planet's climate by the same amount. That is a calibration shift,
not a fix for one planet's tail. It would also bring back, for another 300 Myr, the per-run lottery that PW-1424 A
removed. **Verdict: D is a no-op for the tail. I stopped there, as the brief says. Nothing in `planet/` changed.**

On main, 819014's tail is mostly a lower absolute source than seed 1's, and the two seeds' references are nearly
equal. About half of that gap over 900-1000 Myr is the climate drift's random walk; the other half is slower plates.
The large step every run takes is the land plants' arrival at ~600 Myr: the sink roughly doubles, about 0.7 e-folds
on both seeds. The source decline is much smaller, about 0.3-0.4 e-folds.

## 1. How the references and YARDSTICK are learnt now (main 8640df78)

`planet/tectonics/earth.py::global_temperature`, `::references`, `::YARDSTICK`; `tools/yardstick.py`.

- **Before REF_FREEZE (300 Myr).** Each step learns `learn = [S / drift factor, W_bal]` by an exponential moving
  average with time constant `min(REF_MYR = 100, 10 + t)`. Here S is the raw source (ridge + 20 x nominal arc growth +
  plume, area-weighted). W_bal is the weathering sink taken to the balance climate (shift `co2_term(0) + offset - dT`
  through `temp_response` and `RUNOFF_PER_C`) and grown with the potential plants (`cover_pot`). So the source's
  reference is about the mean raw source over ~200-300 Myr. The stock reads both learnt references: `s = S/Rs`,
  `w = W/Rw`.
- **After REF_FREEZE.** `references(sim)` returns `[Rs, Rs * exp(-YARDSTICK[level])]`. The source's reference is kept
  as learnt; the sink's learnt reference is dropped.
- **YARDSTICK** (L6 1.377, L7 1.618) is the mean, over the paired judge's draws, of the learnt
  `y = ln(Rs / Rw)` at the step at REF_FREEZE. `tools/yardstick.py` reads it from the diag:
  `ln(source_raw/src) - ln(sink_raw/sink)` at t = 300. Its docstring says to re-fit it whenever a change moves the
  size of the weathering or of the outgassing.
- **Consequence.** After 300 Myr, `co2_stock` steps `dX/dt = (s - w co2_law(X)) / CO2_TAU`, and its steady state is
  `co2_law(X) = s / w = S / (W e^Y)`. **Rs cancels.** `sim.refs` has no other reader: only `references` (the stock)
  and `diag.Recorder.temperature` use it. Rs is left with one job: it scales `s` and `w` together, which sets how fast
  the stock relaxes (and how fast CO2 piles up under full ice, where `w ~ 0`).

**Same-state check** (scratch `samestate2.py`; `co2_stock` from one state, Rs scaled by k = 1 / 0.68 / 1.25, the
sink's reference tied to it as on main, 2-Myr steps). At `S/(W e^Y)` = 0.68 the stock reaches ln X -1.3589 for every
k within 3 steps. At 0.95 it reaches -0.2148 within 10 steps. After one step k moves ln X by up to 0.07. That is the
relaxation speed only, gone in about 6-10 Myr.

## 2. The D variants and what each predicts

Every variant below changes Rs after 300 Myr and keeps the sink's reference at `Rs e^-Y`. Each predicts **no change
to CO2 or dT** after 300 Myr on either seed, beyond a relaxation lag of a few Myr. Each predicts a different diag
`src` label.

- **D1, skip the start.** Learn Rs over 300-600 Myr (the mean of the raw parts there). Rs1/Rs = 0.871 on 819014 and
  0.933 on seed 1.
- **D2, running reference.** Rs is an EMA of the raw parts over 300 Myr and never freezes.
- **D3, tied to plate speed.** `Rs x v(t) / v(200-300)`. If the sink's reference were untied from it instead, D3 would
  divide the source by the plate speed. That removes the tectonic outgassing signal the source exists to carry (Mills
  et al. 2017: degassing follows subduction length). It is a clamp, so I rejected it.
- **D4, learn both later** (REF_FREEZE 600, then re-fit YARDSTICK on the judge's draws). This is the only D that
  moves the climate. After 600 Myr every planet still reads `S/(W e^Y_new)`, so the change is one shift of
  `Y_old - Y_new` e-folds for all planets: about 11 C of dT per e-fold at the loop's gain (PW-1158). The gap between
  819014 and seed 1 is unchanged. Between 300 and 600 Myr each run would again balance on its own learnt ratio. That
  is the "dice roll" PW-1424 A removed (sd 0.16 between re-runs of one planet, 1.1 C per 0.1).

## 3. Measured (main 8640df78, L6 1 Gyr, `tools/ice_diag.py --tect`, scratch runs deleted after reading)

Medians per 100 Myr. `driver` is `ln(S/W) - Y`, the stock's own input (its steady state is `ln co2_law(X) = driver`).
`src D1/D2/D3` are the diag label under each variant, computed offline from the same run; the climate is the run's own.

**819014** (learnt y 1.432; Rs 3262, Rw 779):

| | 200-300 | 300-400 | 400-500 | 500-600 | 600-700 | 700-800 | 800-900 | 900-1000 |
|---|---|---|---|---|---|---|---|---|
| src, main | 1.212 | 0.856 | 0.710 | 0.882 | 0.940 | 0.676 | 0.688 | 0.693 |
| src D1 (300-600) | 1.179 | 0.983 | 0.816 | 1.013 | 1.079 | 0.777 | 0.791 | 0.796 |
| src D2 (running EMA) | 1.249 | 0.966 | 0.823 | 1.018 | 1.073 | 0.780 | 0.862 | 0.855 |
| src D3 (x speed) | 1.033 | 0.958 | 0.943 | 1.106 | 1.128 | 1.045 | 0.893 | 0.997 |
| raw parts / Rs (no drift) | 1.111 | 0.883 | 0.764 | 0.940 | 0.933 | 0.711 | 0.730 | 0.757 |
| drift factor | 0.931 | 0.973 | 0.924 | 0.951 | 1.050 | 0.928 | 0.958 | 0.893 |
| sink W / learnt Rw | 0.395 | 0.330 | 0.301 | 0.344 | 0.639 | 0.601 | 0.588 | 0.864 |
| driver ln(S/W) - Y | 0.993 | 1.020 | 0.961 | 1.008 | 0.261 | 0.157 | 0.156 | -0.140 |
| ln X | 2.186 | 2.064 | 1.857 | 2.055 | 1.410 | 0.700 | 0.923 | -0.659 |
| dT (C) | 3.19 | 3.48 | 1.45 | 4.27 | 3.03 | -0.67 | 3.65 | **-3.90** |
| mean plate speed (cm/yr) | 4.65 | 4.25 | 3.82 | 3.71 | 3.34 | 2.76 | 3.05 | 3.22 |

**Seed 1** (learnt y 1.415; Rs 3211, Rw 781):

| | 200-300 | 300-400 | 400-500 | 500-600 | 600-700 | 700-800 | 800-900 | 900-1000 |
|---|---|---|---|---|---|---|---|---|
| src, main | 1.315 | 0.916 | 0.778 | 1.021 | 0.964 | 0.827 | 0.919 | 0.956 |
| src D1 | 1.241 | 0.982 | 0.834 | 1.094 | 1.033 | 0.886 | 0.985 | 1.025 |
| src D2 | 1.384 | 1.015 | 0.885 | 1.125 | 1.045 | 0.900 | 1.009 | 1.061 |
| src D3 | 1.174 | 0.963 | 0.959 | 1.113 | 1.173 | 1.190 | 1.121 | 1.341 |
| raw parts / Rs | 1.105 | 0.926 | 0.870 | 1.086 | 0.915 | 0.858 | 0.875 | 0.906 |
| drift factor | 1.076 | 1.043 | 0.937 | 0.933 | 1.025 | 0.963 | 1.093 | 1.051 |
| sink W / learnt Rw | 0.409 | 0.311 | 0.410 | 0.440 | 0.792 | 0.727 | 0.797 | 0.976 |
| driver | 1.058 | 1.116 | 0.710 | 0.952 | 0.279 | 0.147 | 0.199 | 0.026 |
| ln X | 2.355 | 2.245 | 1.481 | 1.918 | 1.400 | 0.781 | 0.993 | 0.190 |
| dT (C) | 3.94 | 4.35 | 0.21 | 3.49 | 2.39 | 1.29 | 4.27 | 1.99 |
| mean plate speed | 4.44 | 4.19 | 3.82 | 4.11 | 3.69 | 3.37 | 3.59 | 3.31 |

Main's numbers reproduce lane 271's: 819014 src 0.676-0.693 over 700-1000 and dT -3.90 over 900-1000; seed 1
0.83-0.96. Arcs are 90.5-92.8% of the raw source and ridges 5.9-7.3% in every bin of both runs.

What drives the stock, from 200-300 to 900-1000 Myr (ln):

| | driver change | source part ln(src) | sink part -ln(W/Rw) |
|---|---|---|---|
| 819014 | -1.13 | -0.56 | -0.78 |
| seed 1 | -1.03 | -0.32 | -0.87 |

- **The sink, not the source, makes the big step**, and it is the same on both seeds. W/Rw jumps from about 0.34-0.44
  to 0.64-0.79 at 600-700 Myr. That is the land plants arriving (`w_plant` 1.00 -> 2.18-2.22). It rises again over
  900-1000 (`w_plant` 2.30-2.33 -> 2.79-2.82 on both seeds). The design intends this: bare early land holds more CO2
  "until the plants come" (`global_temperature`'s comments). The fast-plate years therefore bias the late climate
  much less than lane 271 thought.
- **819014 against seed 1 over 900-1000**: the driver is -0.140 against +0.026, a 0.17 e-fold gap. Through co2_law's
  slope of ~0.2 that becomes 0.85 e-folds of CO2 (ln X -0.66 against +0.19) and 5.9 C of dT. The source gap is
  ln(0.693/0.956) = -0.32. Of that, the drift is ln(0.893/1.051) = -0.16 and the raw tectonic source is
  ln(0.757/0.906) = -0.18. The sink partly offsets it (-0.12 lower on 819014, because 819014 is colder). In addition,
  819014's weathering land moved warmer over 800-1000 (supply-weighted T 9.1 -> 14.0 C, `w_temp` 1.18 -> 1.56) while
  the planet cooled: the "fresh tropical rock" effect from co2-crash-diagnosis.md section 2.
- **The two references are the same**: Rs 3262 against 3211 and y 1.432 against 1.415. 819014 does not run cold
  because its reference was learnt high. It runs cold because its late absolute source is lower: slower plates
  (2.76-3.22 against 3.31-3.69 cm/yr), plus a drift that wandered low.

## 4. Conclusion and what next

- D does not remove the late cold tail. D1-D3 change no temperature (section 1's cancellation). D4 shifts every
  planet by one amount, leaves the 819014-against-seed-1 gap as it is, and brings back the PW-1424 A lottery over
  300-600 Myr. No sweep was run: the effect is an identity of the code. The same-state check shows it numerically,
  and the offline relabels above give the numbers.
- I did not re-fit YARDSTICK: nothing changed the learnt ratio.
- Lane 271's "the reference is learnt in the fast-plate years, so a late slowdown reads as a cold era" is true of the
  diag's `src` column only. Under PW-1424 A that column is not what the climate reads. Future tail diagnoses should
  read the driver `ln(src/sink)` (= `ln(S/W) - Y` after REF_FREEZE), not `src` alone. The diag now records it as
  `drive` (`planet/tectonics/diag.py::Recorder.temperature`, read-only).
- Option A (an Earth-like ridge share) acts on the absolute source, so unlike D it can move the tail. Two cautions
  from co2-crash-diagnosis.md (section 4, item 5). Ridges move with arcs (ln r 0.92), so at 50% ridges A only damps
  that world's trench-closure drop from 3.6x to 2.8x. And plate-speed falls hit both terms. Here half of 819014's 900-1000 source
  gap is the climate drift, which A does not touch. A needs a YARDSTICK re-fit, because it moves the outgassing's
  size.

Scratch scripts (gone with the scratchpad): `samestate.py`, `samestate2.py`, `analyse.py`, `sinkparts.py`.
Runs: `ice_diag.py --seed {819014,1} --myr 1000 --level 6 --tect` on 8640df78, not registered, deleted after reading.
