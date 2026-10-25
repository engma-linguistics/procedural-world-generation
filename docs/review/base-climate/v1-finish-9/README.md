# v1-finish-9: the plants' CO2 and warming responses (PW-806), and the state of the star work (2026-10-24)

Status: the plant fix is done and committed (offline-measured, tests, veg_check, earth_check, scorecard below). The
in-run pass rates were NOT re-measured: the sweep was stopped when the owner's star-anchor ruling arrived, because the
star changes every run anyway. The star anchor, PW-807 (plant groups on Earth's calendar) and the pass-rate re-measure
are handed off (`issue-tracking/inbox/draft-star-anchor-at-run-end.md`).

## 1. What was steeper than the evidence

Offline, on stored world climates, the sign-off's way (`vegetation.model`, rain held; `diag.py`).

**First, a harness bug in the sign-off's numbers.** `vegco2_full.py` / `vegshift.py` passed the stored cloud layers
(% of sky, 0-100) where `vegetation.model` wants 0..1, so their plants had about half the light. That is why their
absolute numbers "ran ~3x below the stored ones". With cloud / 100 the offline model reproduces the stored Earth
world (34.7% trees offline, 34.8% stored). The diagnosis's direction stands, but its ratios were exaggerated.

On Earth's model climate (577526), the corrected harness, old code:

| case | tree cover | wet equatorial trees (< 10 deg, > 2000 mm) |
|---|---|---|
| 350 ppm, today | 34.7% | 41.6% |
| 280 ppm (Holocene) | 29.5 (85%) | 25.7 (62%) |
| 180 ppm | 17.2 | 10.1 |
| 350 ppm, +3 C | 27.5 | 17.2 |
| 350 ppm, +6 C | 17.0 | 7.7 |
| 185 ppm, -5 C (LGM-like, rain held) | 29.7 | 42.0, of which tropical evergreen 3% |

The mechanism (`gr.py`, tropical evergreen trees on the wet equatorial cells): GPP 1332 g C/m2/yr, maintenance
respiration 1125, NPP ~130. Respiration was a fixed amount per leaf area and per wood, with Q10 = 2 and no
acclimation, so NPP was a small difference of two large numbers:
- **CO2.** 180 ppm cuts C3 GPP by ~40% in the hot tropics (Farquhar's light-limited quantum yield; that part is
  sound), but respiration did not move, so NPP went negative (-197) and the forest went to C4 grass.
- **Warming.** +3 C raised respiration by 23% (Q10 = 2 on the whole growth temperature), GPP fell 3%: NPP -97.

Both amplifiers contradict the physiology:
- Whole-plant respiration is substrate-limited: grown at another CO2 (or temperature), plants keep their
  respiration/photosynthesis ratio, i.e. the carbon-use efficiency NPP/GPP (Gifford 1995, wheat over CO2 and
  temperature; Dewar, Medlyn & McMurtrie 1998/1999; Gifford 2003's review; forests' NPP/GPP ~0.47 across climates,
  Waring et al. 1998). FACE forests' NPP response follows their GPP response (Norby et al. 2005).
- Respiration acclimates to growth temperature: leaf respiration at a set temperature falls in warmer-grown plants
  (Atkin & Tjoelker 2003; Atkin et al. 2015's global data, whose TWQ term cancels about half of the instantaneous
  curve of Heskel et al. 2016, as JULES now uses them, Huntingford et al. 2017); in whole-tree warming experiments
  acclimation cancels ~80% of the rise (Reich et al. 2016); tropical canopy leaves acclimate within days (Slot et al.
  2014).
- Photosynthesis's optimum temperature moves ~0.4-0.6 C per C of growth temperature (Kattge & Knorr 2007;
  Kumarathunge et al. 2019).

What the evidence says the response should look like: the LGM (~185 ppm, colder, drier) shrank tropical forest and
spread C4 grassland at the margins, but Amazonia stayed largely forested and Africa kept refugia (Colinvaux et al.
2000; Mayle et al. 2004; Anhuf et al. 2006; BIOME4's LGM runs need the low CO2 to get the forest losses, Harrison &
Prentice 2003; Prentice et al. 2011). Holocene forests at 280 ppm were close to today's. Paleocene-Eocene tropics at
+5-10 C and high CO2 stayed forested (Jaramillo et al. 2010).

What is real and kept: C3 photosynthesis does collapse toward ~150 ppm (the C3 starvation limit Caldeira & Kasting
1992 used; Sage & Coleman 2001; Gerhart & Ward 2010). The quantum-yield CO2 response, the WUE ~ Ca response (Ci/Ca
stays near constant, Wong et al. 1979) and the C4 envelope shift are unchanged.

## 2. The change (`planet/vegetation.py`)

1. **CO2: the carbon-use efficiency is today's at any CO2.** `_year` also sums the GPP the plant would have at
   today's CA_REF (`gref`: the same month, quantum yield and water cap at CA_REF), and scales the year's respiration
   by GPP / gref. NPP then moves in proportion to GPP. No change at 350 ppm (so no change on Earth).
2. **Respiration acclimates to the growth temperature.** `site()` gives each cell `tg`, the mean of its three warmest
   months (Atkin's TWQ). Each type's respiration rates are those of the type grown where it grows on Earth: `T_GROWN`,
   its cover-weighted TWQ on Earth's model climate (`tref.py`). The month's Q10 term uses
   t - 20 - RESP_ACCLIM (tg - T_GROWN), RESP_ACCLIM = 0.8 (Reich et al. 2016's whole trees; the trait data's ~0.5 to
   full R/P conservation is the range), within ACCLIM_SPAN = 10 C of T_GROWN (acclimation is bounded; that is about
   the span of the controlled-growth and seasonal data).
3. **The growth hump's high-temperature side** (temp[2], temp[3]) moves by PS_ACCLIM = 0.5 of the same bounded
   difference. The cold side stays.

These are three literature numbers, not fitted to tree cover. The span was first set at 6 C (a hot desert's soil
crust, 20 C above the mosses' Earth range, then grew too much cover); 10 C keeps that crust bounded and lets Earth's
tropics acclimate to +6 C. That choice is the one judgement call; 6 C gives the same picture with +6 C warming
weaker (`anchors` at span 6: 16% wet-tropics trees at +6, 24% at 1000 ppm and +6).

## 3. After: Earth's climate (577526), offline (`anchors.txt`)

| case | old: trees / wet-eq | new: trees / wet-eq |
|---|---|---|
| 350 ppm, today | 34.7 / 41.6 | 41.2 / 60.8 |
| 280 ppm (Holocene) | 29.5 / 25.7 | **40.0 (97%) / 54.8 (90%)** |
| 350 ppm, +3 C | 27.5 / 17.2 | 38.0 / 44.6 |
| 350 ppm, +6 C | 17.0 / 7.7 | 33.0 / 28.3 |
| 560 ppm, +3 C | 36.7 / 45.3 | 40.8 / 53.3 |
| 700 ppm, +6 C (Eocene-like) | 28.3 / 24.2 | 37.3 / 41.4 |
| 1000 ppm, +6 C | 33.8 / 36.7 | 38.8 / 44.9 |
| 280 ppm, -4 C | 40.3 / 70.2 | 42.1 / 74.0 |
| 185 ppm, -5 C (LGM-like, rain held) | 29.7 / 42.0 | 41.0 / 72.3 |
| 155 ppm, +4 C (a star-warmed slice) | 4.5 / 2.0 | 23.5 / 10.6 |

- Holocene check (the ticket's ">= ~80% of the 350 ppm cover at 280 ppm"): 97% global, 90% wet tropics.
- The LGM-like case holds rainforest; rain is held, so it overstates (the LGM was drier).
- 155 ppm and +4 C still has little equatorial forest: that is the C3 starvation limit, kept on purpose.
- What is left of the warming response comes from the base climate's dim tropics, not the plants: with the stored
  cloud x 0.6 (about the real equatorial sunshine), the new code gives 86 / 83 / 75% wet-tropics trees at +0 / +3 /
  +6 C and 79% at 180 ppm (the old code: 83 / 69 / 33% and 30%). On the model climate the trees' GPP is ~1350 g C
  against an observed 2300-3500; veg_check's equatorial NPP is 390 against MOD17's 700 on the model climate, 780 on
  the observed one. Draft: `draft-dim-model-tropics-thin-forest-margin.md`.

## 4. The six star-default L7 showcases, offline at their own pCO2 (`offline_before.txt`, `offline_after.txt`)

| world | dT | pCO2 | stored trees / wet-eq | old offline | new offline |
|---|---|---|---|---|---|
| 6fbc2c | +3.8 | 155 | 2.5 / 1.9 | 5.1 / 2.4 | **29.3 / 40.3** |
| a12762 | +4.6 | 142 | 1.7 / 1.3 | 3.6 / 2.0 | 17.3 / 6.5 |
| 067778 | +0.8 | 221 | 11.4 / 3.4 | 16.6 / 6.2 | 22.7 / 24.2 |
| 6909cb | +6.4 | 349 | 20.2 / 8.9 | 25.9 / 14.1 | 34.7 / 35.3 |
| e71172 | +5.5 | 160 | 2.4 / 3.2 | 4.1 / 3.9 | 24.2 / 11.7 |
| 2a7385 (read only) | +6.5 | 277 | 16.6 / 8.2 | 22.8 / 11.8 | 33.5 / 34.4 |
| bdded2 (no star) | -2.0 | 350 | 24.8 / 47.3 | 31.5 / 60.7 | 41.7 / 84.5 |
| Earth 577526 | 0 | 350 | 34.8 / 37.4 | 34.7 / 41.6 | 41.2 / 60.8 |

Against the (now coordinator-set) bar, offline: global 15-40% (diagnostic): 6 of 6 showcases in range (Earth and
bdded2 at 41-42%, just over). Wet equatorial >= ~20% (hard): 4 of 6 pass; a12762 (142 ppm) and e71172 (160 ppm) fail,
both at the C3 starvation limit. These are offline on the stored (old) climates; new makes under the anchored star
will have different pCO2 and are the real test (not done).

## 5. Earth calibration (tools/veg_check.py, world 506694; before -> after)

- Observed climate: potential-vegetation agreement 62.1 -> 61.6%, land NPP 60.6 -> 59.5 Pg C/yr, forest 43.6 -> 43.6
  Mkm2, savanna 22.1 -> 21.5, tundra 11.1 -> 11.3. Model climate: agreement 40.0 -> 39.3%, NPP 44.5 -> 43.3.
- The acclimation reference is Earth's own growth temperatures, so Earth barely moves, as intended.

## 6. Tests and checks

- `uv run pytest -q`: 677 passed. `tests/golden/sim_L4_s1_60myr.json` updated on purpose (the run's vegetation feeds
  its weathering and albedo). No assertion or threshold changed. `test_npp_and_types_on_ideal_climates`'s desert
  cover (< 0.3) is the check that bounded the acclimation (0.28 before, 0.295 after).
- earth_check / scorecard: see section 8.

## 8. earth_check and scorecard

- earth_check (Earth climate with its vegetation feedback): group agreement 71.1% (exact 34.0%), log-rain corr
  0.648, shares A 20.8 / B 20.1 / C 23.9 / D 23.8 / E 11.3: unchanged from the previous entry (71.1 / 33.9 / 0.649).
- scorecard (2 seeds, 1 Gyr, L6, code default star 0.45): seed 1 tree cover 7.2%, NPP 227, dry 33.8%, ice 1.1%;
  seed 2 tree cover 26.3%, NPP 316. The last entry (f7621ad, before the star default and the merge) had seed 1 at
  15.2% trees and dry 23.1%; the two are different trajectories (a different base), so this is not a measured
  effect of the plants. Seed 1's 1 Gyr end is a dry, warm, CO2-low moment; the in-run pass rates still need the
  star-anchored re-measure.

## 7. The star: what is in the branch, and what is not

- `earth.star_control` (PW-791), a labelled, bounded, causal star thermostat, is in the code, OPT-IN and OFF
  (params `star_thermostat` False; the earthlike preset does not set it). Unmeasured:
  `draft-star-thermostat-unmeasured.md`. `launch.sh` is the sweep that was started with it on and stopped.
- The star anchor at the run's end (owner ruling) is not started. Its design question (count the forcing against
  the run's start or against today's Sun; the spin-up references and the faint young Sun) is in
  `draft-star-anchor-at-run-end.md`. Compensations met so far that belong to the old frame: `star_brightening` 0.45,
  `star_age` 0, REF_MYR / REF_FREEZE (references learnt over the first 300 Myr), the criteria's 300 Myr spin-up skip,
  and FLORA_PACE / vegetation.GROUPS fractions (PW-807). None was touched.
- `tools/ice_diag.py --set` now parses bool params.

## Files

`diag.py` (offline tree cover per world, pCO2:shift pairs; CLOUDF scales the cloud), `gr.py` (GPP / respiration
breakdown), `tref.py` (T_GROWN), `ideal.py` (the test's ideal climates), `anchors.sh`, `before_after.sh`
(`before/` is `git archive HEAD planet` of the pre-change code), `launch.sh` (the stopped sweep), and the outputs.
