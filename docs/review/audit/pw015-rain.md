# PW-015: moisture transport, stages 1-2 (with PW-358); stopped before stage 3

*2026-10-16. Proposal: docs/proposals/moisture_transport.md (owner-approved, all six leans). Branch from main
b8872f2. Two model commits: stage 1 (1af9a9b) and stage 2 (ecffcb9).*

## Short answer
- **Stage 1 (built):** the rain kernel runs in physical time with a conservative finite-volume transport. L6 and
  L7 now agree (Earth land P 1137 / 1153 mm; main 993 / 784), and the books close to -0.01..-0.08% of rain.
- **Stage 2 (built), with PW-358:** storm eddies, bulk sea evaporation, and Penman lakes. The storm tracks get
  their moisture (40S -1.01 Sv, sea P 50-60S 882 mm). The deserts dry (Sahara 54 mm) and Koppen exact agreement
  rises to 35.1%. **But the humid subtropics dry out** (SE USA 277 mm, Pampas 217), generated planets get more
  arid (29 -> 36% of land) with less forest, and their ice grows.
- **Stage 3 (not built):** both parts of it need PW-352's warm summers fixed first. The humid east coasts' summers
  are warm in the first-pass air temperatures, not from the evaporative split (section 4), so there was no sound
  fix inside this lane. Following the rules, the lane stops at stage 2's clean boundary. Stages 4-6 were not
  started. Whether to merge stages 1-2 is a needs-decision draft.
- **PW-016:** the spin-up rule is already inert on Earth (since PW-360). But the Atlantic's E-P-R is +0.20 Sv at
  L6, short of the +0.25 the proposal requires: its catchments are too wet.
- **PW-380** (the equator's seasonal swing): seasons() and the air temperatures are untouched here, so it is
  left for a later climate batch.

**Follow-up (section 9):**
- Stage 1 alone is neutral on generated planets. On Earth it is wetter (land +15% at L6).
- Stage 2 is not for merging. A revision (shallow land-sea circulations) recovers the SE USA to 757 mm, but leaves
  the winter coasts, the one-layer column's sea evaporation and drier, icier generated planets.

## 1. What changed (planet/climate.py; tools/moisture_budget.py, tools/earth_check.py; tests)
**Stage 1:**
- `_faces` builds each grid edge's face: length, normal, the centres' distance, the cell areas, and a per-cell
  CSR.
- `face_winds` gives the face wind in m/s (wind 1 = 7 m/s) and the eddy mixing K = 2e5 m2/s x clip(0.12 +
  eddy x B).
- `_transport` folds these into each cell's kept share and each neighbour's share per step, at a CFL step
  (<= 0.95 of a cell's vapour leaves per step). The flux out of one cell is the next cell's gain, so mass is
  kept. The shares are stored as float32, and the gather is fused into one pass per cell, laid out
  [cell, season].
- Rates are shares per RATE_S = 17189 s (one old L6 step), so TUNE keeps its values.
- 20 days of pseudo-time from a start near the steady state (sea at 0.85 q_s, land air 30% saturated). From
  dry land air this takes ~50% longer, and the start doesn't change the answer: Earth regions are within 1.2% of
  80 days.
- `inflow_weights`, `move` and `diff` are gone.

**Stage 2:**
- `storm_eddies`: u_e = -storm_k B q_k grad(T_mass), the moist-EBM closure as a velocity (storm_k 1.3e6 m2/s).
- Sea uptake by the bulk formula, rho C_E U_s (q_s(SST) - q), with C_E 1.2e-3 and the scalar wind with 5 m/s of
  gusts. The kernel's near-surface q fills a vapour column `vap_h_m` = 2 km deep: k_pw/(rho q0), its water per
  unit of near-surface humidity.
  - Reading the proposal's formula literally (a target 0.85 q_s, 1 km) left a sea at its usual humidity
    evaporating nothing. Measured at L6: SE USA 455 mm against 277, Koppen exact 34.5 against 35.1.
- PW-358: `open_water_evap`, Penman's combination equation for lakes (FAO-56 net radiation from the half-year's
  cloud, e_a from the humidity, u2 = 2 m/s), as `lake_evap`.

**Tools:**
- moisture_budget's probe follows the kernel bit for bit. Its face fluxes are exact, and the books report the
  steady state's drift.
- earth_check adds the log-rain correlation and PW-019's flat-ground neighbour ratio.

**New tests:**
- `tests/test_rain_transport.py`: mass kept by any transport step; faces close each cell; no rain from a dry
  column; the same continent rains within 5% at L5 and L6.
- the seam test on the new transport;
- Penman lakes;
- the probe's face fluxes close the budget.
- test_ocean's cloud test: the stratocumulus deck must be > 0.03 cloudier than the western subtropical seas,
  instead of 0.1. The western side's ~3x the rain now brings its own deep cloud.

## 2. Earth, per stage (earth_check; mm/yr; Sv)
| | main L6 | stage 1 L6 | stage 2 L6 | stage 3 gate (not built) | main L7 | stage 1 L7 | stage 2 L7 | obs |
|---|---|---|---|---|---|---|---|---|
| Koppen group / exact % | 71.0 / 32.7 | 70.6 / 30.9 | 70.3 / 35.1 | 69.0 / 34.4 | 69.9 / 33.2 | 70.0 / 30.3 | 69.6 / 34.5 | |
| B share of land % | 20.3 | 18.0 | 29.3 | 33.8 | 24.5 | 17.9 | 29.9 | 30.1 |
| land P | 993 | 1138 | 1200 | 1152 | 784 | 1152 | 1198 | 791 |
| log-rain corr | 0.601 | 0.617 | 0.667 | 0.647 | 0.583 | 0.599 | 0.667 | |
| flat-ground nbr ratio (PW-019) | 1.073 | 1.059 | 1.079 | | 1.041 | 1.035 | 1.043 | |
| Sahara | 326 | 431 | 54 | 58 | 270 | 443 | 49 | 35 |
| Sahel | 2003 | 2369 | 2733 | 2754 | 1391 | 2433 | 2711 | 593 |
| Gobi | 582 | 534 | 556 | 342 | 309 | 457 | 483 | 157 |
| Central Asia | 389 | 432 | 174 | 129 | 330 | 395 | 158 | 209 |
| Australia interior | 831 | 957 | 823 | 707 | 673 | 1005 | 869 | 291 |
| SE USA | 1343 | 1156 | 277 | 110 | 1082 | 1086 | 275 | 1328 |
| SE China | 1118 | 1295 | 1163 | 788 | 916 | 1261 | 1169 | 1462 |
| India | 711 | 723 | 642 | 630 | 588 | 726 | 649 | 1109 |
| Amazon | 2721 | 3089 | 3755 | 3780 | 2058 | 3123 | 3750 | 2335 |
| W Europe | 934 | 1244 | 1436 | 1179 | 813 | 1213 | 1438 | 907 |
| Pampas | 703 | 681 | 217 | 179 | 598 | 702 | 216 | 943 |
| Tibet | 76 | 70 | 39 | 27 | 33 | 54 | 36 | 296 |
| warmest month SE USA / SE China / Pampas C | 29.6 / 29.3 / 30.4 | 29.7 / 29.1 / 30.4 | 31.0 / 29.1 / 31.4 | | | | 30.5 / 28.9 / 31.1 | 25.3 / 24.5 / 25.1 |
| E-P-R Atlantic / Pacific / Indian | +0.06 / +0.24 / +0.25 | +0.07 / +0.36 / +0.35 | +0.20 / +0.47 / +0.48 | | +0.19 / +0.14 / +0.13 | +0.42 / +0.36 / +0.34 | +0.71* / +0.46 / +0.46 | +0.3..+0.6 / ~0 / +0.3..+0.6 |
| Atlantic - Pacific per area mm | -26 | -48 | -16 | | +54 | +111 | +224* | >= +100 needed |
| transport 40S / 50N | -0.54 / +0.28 | -0.66 / +0.43 | -1.01 / +0.80 | -1.03 / +0.88 | -0.29 / +0.14 | -0.66 / +0.43 | -1.01 / +0.80 | -1.39 / +0.52 implied |
| sea P 50-60S | 483 | 492 | 882 | 907 | 524 | 497 | 901 | 1122 |
| sea P 60-70S / 60-70N | 334 / 327 | 322 / 322 | 393 / 402 | | 363 / 351 | 325 / 331 | 389 / 400 | 723 / 905 |
| Antarctic land 70-80S | 174 | 184 | 218 | | 129 | 200 | 216 | ~210 |
| rain efficiency median / worst | 1.62 / 12.0 | 1.67 / 11.2 | 1.47 / 14.6 | 1.39 | 1.62 / 15.6 | 1.65 / 11.2 | 1.47 / 16.6 | 1 |
| mass residue % (Apr-Sep / Oct-Mar) | -0.14 / -0.66 | +0.01 / -0.03 | -0.01 / -0.08 | | +0.04 / -0.26 | -0.01 / -0.04 | -0.05 / -0.12 | |

\* L7's Atlantic is the budget tool's river routing, not the model: E - P is the same at both levels (1.60 Sv),
but at L7 ~0.5 Sv of the Atlantic side's runoff ends in "Med+inland" (draft). Stage-1 columns are with the
final 20-day setting.

**Other numbers:**
- Recycling (stage 2): 31% of land rain is land-evaporated (obs ~40; main 40%). 75% of land evaporation rains on
  land (obs ~57).
- Vapour residence: 7.5 days (obs PW/P 9.0; main 5.7).
- Oct-Mar column vapour: SE USA 3.1 mm (NCEP 17.5; main 6.1), SE China 5.1 (21.3), Great Plains 2.2 (9.2).
  The stage-2 target was >= 70%: not met (draft).
- (P/PW)/obs by region and half-year, stage 2: Sahel Apr-Sep 3.97, Gobi Apr-Sep 4.11, Sahara Oct-Mar 14.6,
  W Siberia Apr-Sep 2.39, Tibet 0.24 / 0.30, SE USA 0.51 / 0.22.

**Acceptance (proposal section 8):**
- **Stage 1:** residue < 0.05% (yes). L6/L7 within 5% on land P (1.3%), B (0.6 points) and the regions (all
  within ~6% except the Gobi -14% and Tibet). PW-019's flat-ground neighbour ratio is already 1.06 by this
  metric (median wetter / drier over flat neighbouring lowland cells; the ticket's 1.5 was one hothouse world's
  basin). On world 592f2a's terrain at L6 its p90 falls 1.31 -> 1.27. The L7 update is 1.6x main's, cold
  (below).
- **Stage 2:**
  - Transport at 40-50 deg: yes.
  - Sea P 50-65S / 50-70N within 30% of GPCP: 50-60S 79% and 50-60N 90% pass; 60-70 deg is ~55% in both
    hemispheres.
  - Antarctic land 70-80S within 30% of ~210: yes.
  - East coasts' winter PW: no.

## 3. Level agreement on a generated planet (PW-290) and cost
- **World 592f2a's terrain** (L7 seed 3199), its own L7 grid against the L6 icosphere's vertices: land rain at the
  shared cells, L7 / L6, median 0.83 (p10 0.66, p90 1.11) on main -> 1.02 (0.94, 1.09) at stage 1. Land P
  873 / 1071 -> 1279 / 1246 mm, arid 29.8 / 26.5 -> 23.3 / 23.8%.
- **Cost** (Earth compute, Threadripper, 8 numba threads):
  - L6: 0.50 s -> 0.62 s.
  - L7: 2.21 s -> 3.47 s (1.57x; the kernel 0.48 -> 1.40 s).
  - The kernel is memory-bound (no fast cells to sub-cycle: the CFL is set by the mixing and the winds
    everywhere).
  - Warm starts in runs would save ~40%, but need earth.py (draft).

## 4. Why stage 3 stopped (PW-352)
**The tried parts** (on stage 2, Earth L6):
- Showers gated by the column's humidity after Bretherton et al. 2004, exp(15.6 (q/qs - 0.8)): the Gobi
  556 -> 342 mm, Central Asia 174 -> 129. But SE USA 277 -> 110, SE China 1163 -> 788 (-32%, outside the
  proposal's +-25%), W Europe -18%. Koppen group 70.3 -> 69.0, exact 35.1 -> 34.4, B 33.8%, log-rain corr
  0.667 -> 0.647.
- The air-mass reference aloft: not tried. Decision 3 makes it conditional on the warm-summer fix, and the
  prototype showed it drying the same regions.

**Where the summer warmth comes from:**
- Warmest month, first pass (before the rain) / final / NCEP: NE USA 28.4 / 27.3 / 21.3 at AET/PET 0.90; SE USA
  30.6 / 31.0 / 25.3 (0.23); SE China 30.2 / 29.1 / 24.5 (0.71); E Australia 29.6 / 29.9 / 23.7; Pampas
  30.9 / 31.5 / 25.2.
- Over 20-50 deg land binned by AET/PET, the warm bias is +0.2 C for deserts and +1.6..+1.9 C at any wetness.
- So a sound Bowen-ratio split would take ~2 C off humid land. The east coasts' +4.6..+6 C is already in the
  first-pass air temperatures (the summer air carried onto them is continental), the air model's problem with
  PW-026's.
- And the kernel never sees the land finish's cooling (its inputs are the first pass).

**Draft:** draft-east-coast-summers-first-pass, for PW-352.

## 5. The probe (`tools/ice_probe.py 0 -6 --regions`, Earth L6, 8 updates)
| | main | stage 1 | stage 2 |
|---|---|---|---|
| dT 0: sea level from ice, m (update 8) / ice share | -35.8 / 2.54% | -36.8 / 2.55% | -45.8 / 3.18% |
| dT 0: Antarctica cells, snow mm | 824, 188 | 830, 211 | 814, 195 |
| dT 0: elsewhere | 51 cells | 52 | 325 cells, 1167 mm of snow (not located) |
| dT -6: m / share | -58.0 / 4.14% | -68.6 / 4.68% | -151.1 / 8.41% (elsewhere 2403 cells: northern sheets) |

PW-313's "steady near 3%" holds at dT 0, and dT -6 now grows LGM-like northern ice (Earth's LGM ~-120 m).

## 6. Generated planets (health --quick, 8 L6 seeds x 500 Myr, `--workers 8 --threads 1`)
docs/review/health-rain-before/ (main b8872f2) and docs/review/health-rain-after/ (stage 2, ecffcb9). Frames
after 50 Myr; per-seed medians, then their mean:

| | before | after |
|---|---|---|
| arid (dry_pct), % of land | 29.3 | 36.1 |
| inland drainage % | 4.6 | 6.7 |
| lakes % of land / largest lake Mkm2 | 0.55 / 0.18 | 0.48 / 0.14 |
| giant-lake frames % (per seed) | 13.6 (16 6 14 9 10 18 22 14) | 14.7 (29 14 21 9 20 5 12 6) |
| global T C / coldest per seed | 14.6 / 2.8-12.0 | 14.0 / 2.7-12.0 |
| land ice % / ice sea level m (median) | 0.86 / -5.6 | 3.46 / -24.8 |
| icehouse spells (ice SL < -50 m) / deepest per seed | 5 / -8..-228 | 16 / -77..-216 |
| tree cover % / NPP g C/m2/yr | 27.0 / 334 | 20.6 / 277 |
| land % | 33.4 | 32.3 |

- More ice is closer to Earth (today's ice is ~-65 m of sea level; PW-308's runs barely glaciated).
- The aridity and the forest loss are stage 2's drier subtropics.
- PW-358 didn't move the giant lakes (draft).
- Scorecard (L6 seeds 1/2 at 1 Gyr; `--jobs 3 --threads 2`):
  - Earth: 71.0 / 32.7 / corr 0.601 -> 70.3 / 35.1 / 0.667.
  - Seed 1: dry 45.0%, trees 10.1%, NPP 341 (main's last: 26.9%, 18.7%, 415).
  - Seed 2: ice 10.6%, NPP 188, trees 19.8 (main's last: 2.5%, 365, 21.7). Single chaotic moments, but the same
    direction as the sweep.

## 7. Vegetation, soils, coasts (Earth L6 worlds made with each code)
| | main | stage 2 |
|---|---|---|
| veg_check (model climate): potential-vegetation agreement | 40.5% | 41.0% |
| land NPP Pg C/yr (target 45-70) / MOD17 r by cell | 47.7 / 0.29 | 38.3 / 0.39 |
| forest (trees >= 60%) / desert and xeric shrub Mkm2 | 42.2 / 18.9 | 32.7 / 33.3 (obs ~25-30) |
| burned area Mkm2/yr (GFED ~4-5) | 4.9 | 3.4 |
| soil_check (model climate): type agreement | 34.2% | 35.2% |
| soil_check (observed climate) | 45.5% | 44.4% (the world's rivers and floods) |
| coastal_check: places as observed | 41 / 55 | 40 / 55 (Guinea-Bissau mangrove 1.0 -> 0.6%) |

The proposal's stage-5 bar for veg_check (>= 47%) isn't met. The deserts grow past Earth's and NPP falls with
the subtropics' rain.

## 8. PW-016
- `moc_spin` 6 / 1 / 30 / 0.5 give the same Earth overturning at L6 and L7 (14.6 Sv, 13.7 Nordic, 0 Labrador,
  0 N Pacific), on main as well.
- On stored generated worlds, removing it changes one of four noticeably (bd9a7a 29.6 -> 26.9 Sv, a northern
  site moving). So it still selects between steady states.
- The condition to remove it isn't met at L6: Atlantic E-P-R +0.20 Sv, -16 mm/yr against the Pacific.
- The Atlantic's E - P is large enough (1.60 Sv). What's missing is drier tropical catchments: its rivers bring
  1.40 Sv against ~0.55.

## Goldens and drafts
Goldens: see the final commit (regenerated after merging main).

Inbox drafts:
- draft-pw015-merge-stages-1-2 (needs-decision)
- draft-east-coast-summers-first-pass (PW-352)
- draft-subtropics-dry-after-bulk-evaporation
- draft-zoom-lakes-penman
- draft-rain-warm-start-in-runs
- draft-pw016-spin-up-status
- draft-moisture-budget-l7-drainage
- draft-pw304-land-books-residue
- draft-pw300-after-pw358


## 9. Follow-up (coordinator, same day): stage 1 alone, and why stage 2 dries the humid subtropics
The coordinator decided not to merge stage 2 as it stood. This section measures stage 1 on its own (1af9a9b),
then reports one real attempt at the subtropics.

### 9.1 Stage 1 alone (1af9a9b; its own code, its own sweep: docs/review/health-rain-s1/)
| Earth (mm/yr) | main L6 | stage 1 L6 | main L7 | stage 1 L7 | obs |
|---|---|---|---|---|---|
| Koppen group / exact % | 71.0 / 32.7 | 70.6 / 30.9 | 69.9 / 33.2 | 70.0 / 30.3 | |
| B share % | 20.3 | 18.0 | 24.5 | 17.9 | 30.1 |
| land P / log-rain corr | 993 / 0.601 | 1138 / 0.617 | 784 / 0.583 | 1152 / 0.599 | 791 |
| Sahara / Sahel / Gobi / C Asia | 326 / 2003 / 582 / 389 | 431 / 2369 / 534 / 432 | 270 / 1391 / 309 / 330 | 443 / 2433 / 457 / 395 | 35 / 593 / 157 / 209 |
| Australia int. / SE USA / SE China / India | 831 / 1343 / 1118 / 711 | 957 / 1156 / 1295 / 723 | 673 / 1082 / 916 / 588 | 1005 / 1086 / 1261 / 726 | 291 / 1328 / 1462 / 1109 |
| Amazon / W Europe / Pampas / W Siberia | 2721 / 934 / 703 / 426 | 3089 / 1244 / 681 / 583 | 2058 / 813 / 598 / 304 | 3123 / 1213 / 702 / 574 | 2335 / 907 / 943 / 503 |
| residue % | -0.14 / -0.66 | +0.01 / -0.03 | +0.04 / -0.26 | -0.01 / -0.04 | |

- **Ice probe:** dT 0 holds 2.55% (main 2.54); dT -6 -69 m (main -58).
- **L7 update:** 2.21 -> 3.60 s (cold).
- **On world 592f2a's terrain:** L7/L6 land rain 0.83 -> 1.02.

**Generated planets** (health --quick, 8 L6 seeds x 500 Myr; per-seed medians after 50 Myr, then the mean):

| | main | stage 1 | stage 2 | stage 2 revised |
|---|---|---|---|---|
| arid % of land | 29.3 | 27.8 | 36.1 | 37.8 |
| tree cover % / NPP | 27.0 / 334 | 26.0 / 321 | 20.6 / 277 | 21.3 / 304 |
| land ice % / ice sea level m | 0.86 / -5.6 | 1.68 / -12.9 | 3.46 / -24.8 | 3.85 / -26.8 |
| icehouse spells / deepest per seed m | 5 / -8..-228 | 9 / -11..-217 | 16 / -77..-216 | 11 / -42..-491 |
| giant-lake frames % | 13.6 | 10.3 | 14.7 | 14.1 |
| inland drainage % / lakes % | 4.6 / 0.55 | 4.6 / 0.56 | 6.7 / 0.48 | 7.0 / 0.45 |

**Verdict on stage 1:**
- On generated planets it stands on its own: nothing moves outside seed noise but a little more ice.
- On Earth it brings what it promises: L6 = L7, the books closed, a better log-rain correlation.
- But Earth's land is ~15% wetter at L6 than main, and ~47% wetter at L7 (main's L7 was right only through its
  level-dependent dryness). Koppen exact falls 1.8 points at L6 and 2.9 at L7, and the dry interiors get wetter
  (Sahara 326 -> 431).
- That is the proposal's warning ("S1 alone adds 15% of land rain at L6"). It is a smaller regression than
  stage 2's, but a real one on Earth. The coordinator's call.
- Stage 1 needs nothing from stage 2. Cherry-picking it means regenerating the goldens (climate_L4,
  sim_L4_s1_60myr) and re-running the zoom tests.

### 9.2 Why stage 2 dries the humid subtropics, and the fix tried (326e482)
On the coasts (tools: a box diagnostic on the probe), stage 2, Earth L6:
- **The cold half (Oct-Mar in the north, Apr-Sep in the south):** the mean vapour wind blows offshore on every
  subtropical east coast:
  - SE USA 3.7 m/s from the NW, SE China 4.2 from the N, the Pampas and E Australia ~3.5 from the W.
  - The storms' eddy velocity there is 0.2-0.7 m/s.
  - So the land columns sit at 11-28% of saturation (PW: SE USA 2.7 vs NCEP 17.4 mm, SE China 4.6 vs 22.5,
    Pampas 5.6 vs 18.2).
  - Part of that offshore wind is the land-sea circulation: the continent's winter high draining off. The
    vapour rode it at full strength, though a cold dome is 1-2 km deep and the vapour above rides the deeper
    flow (DJF 850 hPa over the Gulf coast is south-westerly).
- **The warm half:** the SE USA has its onshore southerlies (5 m/s), but they feed it from a Gulf/Sargasso column
  ~25% short of NCEP's (q/qs 0.57).

**Fix:** the vapour rides only part of a shallow land-sea circulation. This is the proposal's stage 4, extended
from heat lows to winter highs:
- `rain_phases`: a first kernel phase gives the ground's wetness; the second rides v_belts + s (v - v_belts).
- s = 1 at sea; over a land low (warmer than its latitude), max(0.53, AET/PET smoothed over 800 km); over a land
  high, 0.53 (= 1 - exp(-1.5 km / 2 km), the share of the vapour column a 1.5 km circulation carries).
- The second phase carries the first's vapour and running means: restarted, the L4 books were -2 cm/yr; carried,
  -0.04.

**Results:**

| Earth L6 / L7 | main | stage 2 | stage 2 revised (L6 / L7) |
|---|---|---|---|
| Koppen group / exact % | 71.0 / 32.7 | 70.3 / 35.1 | 72.2 / 36.2 (71.4 / 35.6) |
| B % / land P / log-rain corr | 20.3 / 993 / 0.601 | 29.3 / 1200 / 0.667 | 31.0 / 1153 / 0.685 (31.4 / 1152 / 0.686) |
| SE USA / Pampas | 1343 / 703 | 277 / 217 | 757 / 237 (886 / 233) |
| Sahel / Australia int. / Gobi / C Asia | 2003 / 831 / 582 / 389 | 2733 / 823 / 556 / 174 | 1975 / 463 / 196 / 243 |
| SE China / India / Tibet | 1118 / 711 / 76 | 1163 / 642 / 39 | 1266 / 551 / 12 |
| Amazon / W Europe / W Siberia | 2721 / 934 / 426 | 3755 / 1436 / 796 | 3597 / 1498 / 885 |
| veg_check: agreement / NPP Pg C/yr / desert Mkm2 | 40.5 / 47.7 / 18.9 | 41.0 / 38.3 / 33.3 | 41.7 / 37.9 / 35.0 |

The ice probe is as stage 2 (dT 0 3.20%, dT -6 -149 m). The L7 update is 3.54 s.

Also tried and dropped: an eddy closure on the actual vapour's gradient, -K grad(Q) with Q the vapour over
800 km, written as a velocity (one extra phase). The SE USA 277 -> 323 and the Pampas -> 369 improved, but the
Gobi got wetter again (556 -> 752); with the shallow circulations it gave SE USA 815, Pampas 355, Gobi 432.

**What is left, and why I stopped:**
- The revision fixes the SE USA's summer (1752 vs obs 1323 in Apr-Sep), the Sahel, Australia and the Gobi.
- Its winter is still 4% of observed: the westerlies themselves blow offshore, and the saturation-gradient eddies
  can't carry the Gulf's vapour in. The Pampas and E Australia have the same winter problem.
- India (551) and Tibet (12) get drier, and the wet tropics and the mid-latitude land stay too wet (W Europe
  1498, land 50-60N 1175 vs GPCC 584).
- Under these sits the one-layer column. With the bulk formula, the subtropical seas' columns run at q/qs
  0.5-0.6, so their own rain is low (20-40 deg sea P ~300-450 vs 700-1160) and the land takes the global mean's
  share: land P 1153 vs 791.
  - Real surface air over the sea stays at ~0.8 of saturation under a dry free troposphere. One layer can't
    hold both (proposal decision 1, option C's "needs a second layer").
- **On generated planets the revision is still drier and icier than main:** arid 29 -> 38%, tree cover 27 -> 21%,
  NPP 334 -> 304. The deepest icehouse is -491 m (seed 2, past PW-240's -250 m worst case).
- So stage 2 isn't sound yet, even revised. The revision is committed on the branch (326e482) for the next
  attempt, not for merging. Stage 1 is the merge candidate.

## 10. Option A: a boundary layer under the column (design, 2026-10-16; coordinator's go-ahead)
**Why.** The one-layer column makes the bulk formula see the whole column's humidity. Over the subtropical seas
real surface air stays at ~0.8 of saturation under a dry free troposphere, so E is driven by that small,
steady surface deficit. The column can't hold both. The coordinator adds a second claim, to test: a shallow
moist layer moving on the surface wind, under a free troposphere on the deeper flow, carries winter Gulf and
Pampas vapour inland (the low-level jets under the offshore westerlies). A caution before testing it: the
model's winter surface wind over the SE USA is the continent's own offshore outflow (it has no winter
subtropical oceanic highs, so no southerly return flow there). The claim stands or falls on that wind.

**State.** Per cell and half-year, two vapour amounts in the kernel's column units: m_b in the boundary layer
(the lowest h_b = 1 km) and m_f in the free troposphere above (their sum is the old column m).
- A column at one relative humidity holds the share w_b = 1 - exp(-h_b / H) = 0.39 (H = VAPOUR_H_M = 2 km,
  the vapour's scale height) in the boundary layer, and w_f = 0.61 above.
- So each layer's humidity in near-surface units is q_b = m_b / w_b and q_f = m_f / w_f, each read against the
  same capacity qs.

**Each time step:**
1. **Transport**, the same conservative finite-volume scheme, once per layer:
   - The boundary layer rides the surface wind: the climate's wind_jul / wind_jan before the polar drift
     correction, all of the land-sea circulations.
   - The free troposphere rides the wind belts plus the deep part of the land-sea wind: a wet low's (its
     ground's AET/PET, from the first phase), none of a high's or a dry heat low's.
   - The storms' eddies and the background mixing act on both.
   - This replaces stage 4's single share SHALLOW_S: the shallowness is now the layer itself.
2. **Sources**, both into the boundary layer:
   - the sea by the bulk formula against the boundary layer's humidity: dm_b/dt = C_E U_s (q_s(SST) - q_b) / H;
   - the land's evaporation.
3. **Exchange**: entrainment at the boundary layer's top, dm_b/dt = -w_e (q_b - q_f) / H and the reverse for
   m_f, with w_e = 5 mm/s (subtropical boundary-layer entrainment ~3-8 mm/s). Deep convection vents the
   boundary layer too: the showers' rain takes its water from both layers in proportion to their content, as
   the rest of the rain does.
4. **Rain**, the stage-2 scheme per layer, unchanged in its constants:
   - oversaturation and the large-scale rain on each layer's own vapour and humidity (drizzle and fronts in a
     humid boundary layer under a dry free troposphere);
   - showers triggered by the boundary layer's moist static energy (the surface air's humidity q_b), gated
     and fed by the whole column.

**The books.** Both transports are conservative, and the exchange moves water between layers. So the sum's
books close as before.

**Cost.** Two gathers per step instead of one: the kernel ~1.6-2x, L7 update estimated ~4-4.5 s against the
2x bar of 4.4 s. If it is over, the first phase (only for the ground's wetness) runs one layer.

**Tuning, at most three rounds, nudges only:** w_e and h_b within their physical ranges. Nothing Earth-specific.

**The probe** (tools/moisture_budget.py) follows bit for bit, with its tracers carried in both layers.
