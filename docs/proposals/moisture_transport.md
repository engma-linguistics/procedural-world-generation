# Moisture transport: diagnosis (PW-014) and redesign (PW-015), for owner review

*2026-10-16. Epic PW-013. Tool: `tools/moisture_budget.py` (Earth reports in `docs/review/moisture-budget-2026-10-16/`). Prototype: local branch `pw015-prototype`, a monkeypatch of the rain kernel (nothing under `planet/` changed). Owner decisions are in §9.*

**In one paragraph:** the vapour mostly goes to the right places. What's wrong is how readily it rains and over what distance.
- Over dry and high interiors the column vapour is within ~30% of the reanalysis, but it rains 2–8× too efficiently. The showers fire on little moisture because their trigger compares hot summer ground with air aloft that follows the latitude's sea.
- The kernel's rates are per cell rather than per unit time, so at L7 the vapour rains out in half the distance (PW-290).
- The storms carry almost no vapour poleward: their mixing is capped at ~2×10⁵ m²/s, and the open sea refills the air to 85% of saturation at every step. So the storm-track seas rain what they evaporate rather than what converges on them (PW-332's 0.4 of GPCP).
- The land–sea wind carries sea vapour deep into desert heat lows (Gobi, Australia, Sahel), while India's monsoon stays weak.
- The Atlantic isn't saltier than the Pacific because its catchments are too wet: they return 0.84 Sv of rivers against ~0.55 observed. The vapour flux across Central America is right (0.24 Sv), and the kernel's mass leak is small (<1% of rain).

The redesign keeps the structure (column vapour carried along the seasonal wind, with E as the source and P as the sink) and makes five changes:
1. physical time and a conservative finite-volume transport;
2. a storm-eddy flux down the air mass's saturation gradient;
3. sea evaporation from the bulk formula instead of an instant refill;
4. showers that need a humid column, against a reference aloft that follows the air mass;
5. vapour riding only part of a dry heat low's shallow inflow.

In the prototype each change moves its own symptoms by about the right amount, and L6 and L7 agree. It also shows trade-offs that must be calibrated together, so the work is one branch with staged commits, not a series of merges.

---

## 1. The tool
`PYTHONPATH=. uv run python tools/moisture_budget.py --level 6 [--json f]` (~10 s).
- **How it runs:** it makes Earth's climate as `earth_check` does and records the rain kernel's inputs. It then re-runs the kernel in an instrumented copy (`_probe`), which `tests/test_moisture_budget.py` keeps bit-identical to `climate._rain`. The copy adds tagged tracers, splits each cell's rain into its parts and gives the edge fluxes.
- **What it reports:** basin E, P and rivers; where each drainage basin's evaporation rains and the flux across the divides; northward transport (advection and eddies); zonal E−P; nine paths inland; residence and recycling; the kernel's terms per region; the mass residue.
- **New data:** NCEP/NCAR 1991–2020 latent heat flux, precipitation and precipitable water (NOAA PSL, public domain, ~1 MB each; `h5_reader` now reads PSL's netCDF-4). NCEP's E runs high, so the transports implied by NCEP E − GPCP P are upper bounds. Published budgets are quoted alongside.

## 2. What's wrong, ranked (Earth L6, main cc431ed)

### 2.1 Interiors rain too efficiently; their vapour is about right (dry interiors: PW-305, PW-228)
PW is the column's vapour (the kernel's vapour × 9.5 mm per unit, fitted over the open sea), against NCEP's. Efficiency is P/PW, against the observed (GPCC/NCEP).

| region, half-year | P model / obs (mm/yr) | PW model / obs (mm) | (P/PW) / obs | showers' share | land-evaporated |
|---|---|---|---|---|---|
| Sahara, Apr–Sep | 596 / 44 | 27 / 17 | **8.2** | 62% | 36% |
| Gobi, Apr–Sep | 1144 / 278 | 12.6 / 12.5 | **4.1** | 92% | 74% |
| Central Asia, Apr–Sep | 531 / 173 | 13.6 / 15.9 | 3.6 | 87% | 53% |
| Sahel, Apr–Sep | 3927 / 1108 | 39 / 35 | 3.2 | 74% | 65% |
| Australia interior, Oct–Mar | 1510 / 431 | 33 / 25 | 2.7 | 78% | 49% |
| W Siberia, Apr–Sep | 661 / 638 | **9.8 / 17.2** | 1.8 | 86% | 82% |
| Amazon (Oct–Mar) / SE China (Apr–Sep) | 3692 / 2771, 1959 / 2131 | 42 / 48, 34 / 42 | 1.5, 1.1 | 63%, 81% | 46%, 24% |
| Tibet, Apr–Sep | 141 / 531 | 4.9 / 6.4 | **0.35** | 87% | 46% |

- **By distance from the sea:** land PW is within 10% of NCEP's at every distance, but the ratio of rain to GPCC rises from 1.00 at the coast to 1.6 at 1500–2500 km and 3.3 beyond.
- **N Eurasia gets its summer rain for the wrong reason:** half the vapour, twice the efficiency.
- **The trigger.** Showers make 62–92% of the interiors' rain. They fire when `mse_t + tcor + LQ·q > mse_thr`, and `mse_thr` follows the latitude's sea, levelled in the tropics. Its dry part:
  - is −29 to −42 °C in the tropics;
  - is only −6 to −13 °C over summer continents poleward of ~30° (Gobi −7.8, W Siberia −6.5, Central Asia −11.5), so ~10 °C of LQ·q fires a shower;
  - and no humidity gate applies to showers (the large-scale rain has `rh^3`).
- **Recycling is too local:** 73% of land evaporation rains on land, against 57% observed (van der Ent et al. 2010).

### 2.2 Rates per cell, not per unit time: L7 rains out in half the distance (PW-290)
- **Cause:** every rain-out share (`base`, `cv`, `fex`) and the mixing (`diff`) is per iteration, and an iteration moves the air one cell.
  - The vapour lives ~29 iterations at both levels: 5.7 days and 2300 km at L6, 3.1 days and 1260 km at L7.
  - Observed: PW/P = 9.0 days.
- **Earth, L6 → L7:** land P 995 → 787 mm, B share 20.3 → 24.4%, Central America 0.24 → 0.14 Sv, 40S transport −0.53 → −0.29 Sv.
- **With per-second rates (prototype S1)** the two levels agree to ~2%.

### 2.3 Storms carry no vapour; the sea is pinned to its saturation (PW-332, PW-313, winter east coasts)
Northward vapour transport (Sv), model (its eddy part) against what NCEP E − GPCP P implies:

| | 60S | 50S | 40S | 30S | 30N | 40N | 50N | 60N |
|---|---|---|---|---|---|---|---|---|
| model | −0.04 (−0.01) | −0.30 (−0.01) | −0.54 (−0.02) | +0.02 | +0.06 | +0.48 (+0.02) | +0.28 (+0.01) | +0.04 |
| implied | −0.37 | −0.99 | −1.39 | −1.24 | +0.72 | +0.83 | +0.52 | +0.26 |

- **The eddies carry ≤0.02 Sv anywhere.** `diff = clip(0.12 + eddy·B, 0, 1)` saturates at one neighbour mix per step, which is K ≈ 2×10⁵ m²/s at L6. Storm-track diffusivities are ~10⁶ (diffusive moist energy-balance models: Frierson et al. 2007, Hwang & Frierson 2010, Siler et al. 2018).
- **The open sea refills the air to `rh·qs(sst)` at every step.** Its E is whatever the refill takes:
  - at 50–60S that is 143 mm/yr against NCEP's 408, and sea P is 484 against GPCP's 1122;
  - the subtropics export vapour only equatorward.
- **Winter vapour never reaches the subtropical east coasts or the plains.** Oct–Mar PW: SE USA 6.1 vs 17.5 mm (P 330 vs 1334 mm/yr), SE China 8.0 vs 21.3 (P 312 vs 794), Great Plains 2.7 vs 9.2. Real winter rain there is cyclones drawing warm-sea air poleward, an eddy flux.

### 2.4 The land–sea wind feeds desert heat lows; India's monsoon is weak (Sahel, Australia, Gobi; PW-233)
- **West Africa, Apr–Sep:** P at 250 / 750 / 1250 / 1750 km inland is 3974 / 4940 / 2656 / 506 mm, against 2171 / 1628 / 463 / 112. The belt reaches ~500 km too far north at 2–6× the intensity, with PW only 1.3× NCEP's.
- **The Ganges plain, Apr–Sep:** westward the model's PW falls 25 → 16 mm where NCEP's stays at 32–36, and P falls 1133 → 61 against 2666 → 834. The wind there moves 0.27 cells per step (PW-233).
- **Why:** `monsoon_wind` makes hot ground a low that pulls in sea air, and the vapour rides all of it. Real heat lows (Sahara, Australia, Arabia, Thar) are shallow: a 1–2 km inflow under subsiding air.
- **Prototype:** riding half of the land–sea part (on S1) takes the Gobi 533 → 158 mm (observed 157) and Australia's interior 969 → 277 (291), but India 713 → 534 and SE China 1311 → 717. A share set by the ground's wetness keeps most of the real monsoons (§4).

### 2.5 Why the Atlantic isn't saltier than the Pacific (PW-016)

| basin (Sv; + loses water to the air) | E − P | rivers (open basins) | E − P − R | observed E − P − R |
|---|---|---|---|---|
| Atlantic | 0.90 (NCEP − GPCP 1.13) | 0.84 (~0.55, Dai & Trenberth 2002) | +0.06 (+0.03 with the Arctic) | +0.3..+0.6 |
| Pacific | 0.51 | 0.27 | +0.24 | ~0 to −0.3 |
| Indian | 0.43 | 0.18 | +0.25 | +0.3..+0.6 |

- **Per area the Pacific is the more evaporative basin:** +54 mm/yr, against the Atlantic's +27. Hence the spin-up rule.
- **Central America is right:** +0.24 Sv westward, against ~0.25 (Zaucker & Broecker 1992).
- **So the contrast is lost on land.**
  - The Atlantic's catchments are too wet (Amazon coast 2.3×, Sahel 3.4×), and they gain 0.18 Sv across Africa from the Indian Ocean.
  - All the land returns 1.67 Sv of rivers, against ~1.2 observed (plus 0.17 Sv from closed basins). The tropical land is too wet by about what the storm-track seas lack, since the global mean is held at 1000 mm.

### 2.6 What is not wrong
- **The books (PW-304):** the steady-state residue is −0.14 / −0.65% of rain (Apr–Sep / Oct–Mar) at L6 and +0.04 / −0.25% at L7, ~0.5–1 cm/yr over the sea. It comes from outflow shares that don't sum to 1 and from asymmetric mixing. A conservative transport removes it for free, but it causes none of the symptoms.
- **The orographic time scale:** a physical 3000 s for the oversaturation (Smith & Barstad 2004), instead of `fex`, moves no region by more than ~15% at L6.

## 3. The redesign
It keeps one column vapour per cell and half-year, carried to a steady state with sea and land sources and rain sinks. It keeps the renormalisation to 1000 mm × e^(0.03 dT), which stands for the energy limit on global evaporation; a one-layer model can't compute that limit.

1. **Physical time and a conservative transport** (§2.2, PW-304, PW-019).
   - Upwind finite-volume fluxes through each cell face, with true face lengths, normals and cell areas, and the face wind in m/s (wind 1 = 7 m/s).
   - Pseudo-time steps at a CFL-limited dt (L6 ~4200 s, L7 ~1550 s) over 30 days, or ~10 days from the last update's vapour in runs.
   - Every rate in 1/s: today's per-iteration value ÷ one L6 iteration. Background mixing becomes K = 2×10⁵ m²/s × clip(0.12 + B).
   - This replaces `inflow_weights`, `move` and `diff`. Mass is exact, and a uniform wind has no divergence on the seams.
2. **Storm eddies** (§2.3).
   - An eddy velocity u_e = −K_e·q_k·∇T_mass, with K_e ≈ 1.3×10⁶ m²/s × storminess B, added to the face wind. This is the moist-EBM closure (flux ≈ −K∇(rh·q_s)), applied to the actual vapour.
   - As an advection it keeps the advective time step. A diffusion this large would need dt ∝ h² (16 sub-steps at L7).
3. **Bulk sea evaporation** (§2.3).
   - E = (rh·qs(SST) − q)·U_s / (τ_E·U_ref) through the open-water share, with τ_E = h_BL/(C_E·U_ref) ≈ 1.2×10⁵ s (a 1 km boundary layer, C_E 1.2×10⁻³).
   - U_s is the scalar wind: the mean plus ~5 m/s of weather. The vector mean is near zero under the subtropical highs.
   - Air can then reach a storm-track sea moister than the sea's own saturation, and the convergence rains there.
4. **Rain efficiency** (§2.1).
   - Showers need a humid column, as the large-scale rain does: a steep pickup above q/qs ~0.75–0.85, after the observed rise of rain with column humidity (Bretherton et al. 2004, Neelin et al. 2009).
   - Poleward of the tropics' even-temperature belt, the trigger's reference aloft becomes the warmer of the latitude's sea and the 1500 km air mass over land and sea.
   - PW-305's E1 mixed layer stays a candidate.
5. **Shallow heat lows** (§2.4).
   - The vapour rides the belts' wind plus a share s of the land–sea part. s is 1 at sea; over land it is the ground's AET/PET (smoothed over 800 km, at least 0.3) from the first pass (`coupled_climate` already computes twice).
   - The air temperatures keep the full wind, as with PW-332's polar drift.

Unchanged: land evaporation (PW-266's Budyko, so the books stay closed), the leads (PW-308), the ice-surface lift (PW-332), the storms' spread of frontal rain, clouds. `vapour_mixed` may become unnecessary; check.

## 4. Prototype (Earth L6; mm/yr; transport in Sv)
"Humid showers": q/qs pickup, power 12 above 0.85. "Air-mass trigger" also has the cubic shower gate. "All five" uses the gusty bulk E.

| variant | Köppen group / exact | B % | land P | Sahara | Austr. int. | Gobi | C Asia | Sahel | Amazon | India | SE China | SE USA | 40S / 50N | sea P 50–60S |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| observed | | 30.1 | 791 | 35 | 291 | 157 | 209 | 593 | 2335 | 1109 | 1462 | 1328 | −1.4 / +0.5 | 1122 |
| main | 71.0 / 32.7 | 20.3 | 995 | 328 | 838 | 582 | 390 | 2009 | 2721 | 713 | 1135 | 1348 | −0.53 / +0.29 | 484 |
| main, L7 | 69.9 / 33.1 | 24.4 | 787 | 271 | 679 | 309 | 331 | 1402 | 2058 | 592 | 930 | 1090 | −0.29 / +0.15 | 524 |
| S1 physical time | 70.4 / 30.6 | 18.0 | 1141 | 434 | 969 | 533 | 430 | 2381 | 3091 | 713 | 1311 | 1158 | −0.66 / +0.45 | 493 |
| S1, L7 | 69.9 / 30.3 | 17.9 | 1155 | 447 | 1015 | 457 | 394 | 2442 | 3125 | 716 | 1275 | 1088 | −0.67 / +0.45 | 498 |
| S1 + storm eddies | 70.8 / 32.5 | 19.2 | 1127 | 379 | 855 | 487 | 426 | 2320 | 3066 | 698 | 1293 | 1128 | −0.77 / +0.53 | 524 |
| S1 + bulk sea E | 70.2 / 34.6 | 28.6 | 1284 | 63 | 1015 | 695 | 218 | 2982 | 3965 | 711 | 1267 | 207 | −0.97 / +0.85 | 817 |
| S1 + humid showers | 70.3 / 32.2 | 25.0 | 1073 | 353 | 892 | 378 | 209 | 2510 | 3140 | 672 | 961 | 522 | −0.68 / +0.49 | 506 |
| S1 + eddies + air-mass trigger | 70.5 / 32.9 | 24.3 | 1097 | 352 | 855 | 321 | 210 | 2493 | 3210 | 709 | 895 | 546 | −0.84 / +0.65 | 539 |
| S1 + shallow heat lows | 70.6 / 33.8 | 24.9 | 1042 | 171 | 355 | 114 | 746 | 1857 | 3082 | 613 | 1124 | 844 | −0.70 / +0.45 | 512 |
| all five | 69.7 / 36.0 | 34.3 | 1057 | 70 | 291 | 85 | 277 | 1918 | 3720 | 671 | 717 | 294 | −1.00 / +0.82 | 752 |

How to read it:
- **Level independence holds:** shallow heat lows at L7 is within 10% of L6 everywhere.
- **Each change moves its own symptoms:**
  - the bulk sea E: the storm tracks and the hot deserts;
  - the humid showers and the air-mass trigger: the mid-latitude summer interiors (Central Asia 210 against 209; also the Plains, E Russia and W Europe, in the report);
  - the shallow heat lows: the Gobi and Australia.
- **Together:** exact Köppen agreement 36% (main 32.7), and the deserts, the Gobi and Central Asia on their observations.
- **Not shippable as is.**
  - Under the fixed global mean, what the interiors lose goes to the wet tropics (Amazon 3720).
  - The humid-subtropical east coasts and the Pampas dry out (SE USA 294, SE China 717, Pampas 262). Their summers run 4–6 °C warm, which an air-mass reference stabilises (draft filed), and the subtropical highs' western flanks carry too little vapour poleward (30N +0.2 Sv against +0.7).
  - The Sahel and the Amazon coast move under nothing tried: their convergence needs its own look in step 5.
- **S1 alone adds 15% of land rain at L6.** The face winds no longer gather vapour where the wind slows at a coast. So S1 is the base the other changes are calibrated on, not a merge of its own.

## 5. How it fixes each symptom

| symptom (ticket) | cause | change |
|---|---|---|
| dry interiors too wet (PW-305, PW-228) | 2.1, 2.4 | 4, 5, 3 |
| L7 drier than L6 (PW-290) | 2.2 | 1 |
| mass leak (PW-304); patchy rain, streaks (PW-019) | 2.6 | 1 |
| storm-track seas, Antarctic margins at ~0.4–0.5 of GPCP (PW-332, PW-313) | 2.3 | 2, 3 |
| winter rain missing on the SE USA, SE China, plains (new) | 2.3 | 2, 3 |
| weak monsoons, Ganges ~10× small (PW-233) | 2.4 | 5 + PW-233's wind |
| Atlantic not saltier (PW-016) | 2.5 | 4, 5, then PW-016 |
| winter maritime air inland (PW-026) | vapour inland about right (Eurasia 50–60N PW e-fold 5118 km vs 5806); the coast's rain 0.35–0.6 of GPCC, 1500–5000 km 1.0–1.6× | 4 for the rain; the cold stays PW-026's |

## 6. Cost
The prototype is unoptimised:
- **L6:** a climate update takes 0.41 → 0.69 s (0.48 s from a 10-day warm start). The kernel takes 637 steps against 160 iterations today.
- **L7:** 1.9 → 4.5 s (2.7 s warm), 1696 steps against 280.
- **In runs (warm):** ~+0.8 s per L7 update, ~+3–4 min per Gyr; L7 runs take ~20–25 min/Gyr.
- **Cold starts** (worlds, zooms, time zooms): +0.3 s at L6, +2.6 s at L7.
- **Savings left:** fuse the edge and cell passes, and sub-cycle the few fastest cells.

## 7. The spin-up rule (PW-016) and the land mask (PW-307)
- **PW-016:** the spin-up rule can go once the Atlantic is net-evaporative by itself: E−P−R ≥ +0.25 Sv, and per area ≥ 100 mm/yr above the Pacific's, at L6 and L7. Then remove `moc_spin`. Sinking should start in the Nordic and Labrador seas, none in the North Pacific, ~10–20 Sv. The prototype reaches only +0.07..+0.14 Sv: the Atlantic's tropical catchments stay too wet.
- **PW-307, first:** the rewrite changes `climate.rain`'s interface and `_season_inputs`' land/sea logic, so write it once against the mask. PW-307 is output-neutral on ice-free planets and on today's Earth (`earth_data` floors sub-sea beds under ice at +1 m), and it is a whole fix that can merge alone.

## 8. Steps (one branch, a commit each with its numbers; merged as PW-015 when step 5 passes)
0. **PW-307 land mask** (m). Earth_check and goldens unchanged except on worlds with grounded ice on sub-sea beds.
1. **Physical-time conservative kernel** (m).
   - Residue < 0.05% of rain.
   - L6 and L7 within 5% on land P, B share and the regions.
   - PW-019's flat-ground neighbour ratio ≤ 1.25 (today 1.5).
   - An L7 update ≤ 1.6× today's, warm.
2. **Storm eddies + bulk sea E** (m).
   - Poleward transport at 40–50° ≥ 70% of the implied (40S ≤ −0.95, 50N ≥ +0.35 Sv).
   - Sea P 50–65S and 50–70N within 30% of GPCP.
   - Antarctic land 70–80S within 30% of 210 mm.
   - Oct–Mar PW of the SE USA, SE China and the Plains ≥ 70% of NCEP's.
3. **Rain efficiency, with the warm-summer fix** (m).
   - (P/PW)/obs within 0.5–2 for every probe region and half (today 0.35–12).
   - Sahara ≤ 100, Gobi and Central Asia ≤ 300 mm.
   - Amazon, SE China, India and W Europe within ±25% of today.
4. **Shallow heat lows** (s).
   - Australia interior ≤ 450 mm.
   - West Africa at 1250 km ≤ 2× GPCC (today 5.7×); the Sahel ≤ 1200 mm.
   - India not drier.
5. **Calibrate and check** (m).
   - Köppen group ≥ 71%, exact ≥ 36%, B 26–33%, land P 700–900 mm.
   - veg_check ≥ 47%.
   - health --quick: L6 and L7 arid shares within 3 points.
   - The PW-313 probe steady near 3%.
   - Atlantic E−P−R ≥ +0.25 Sv.
6. **PW-016** (m), as §7.

## 9. Decisions for the owner
1. **Sea evaporation.**
   - (A) Instant refill plus eddies: small gains (40S −0.77 Sv).
   - (B) The bulk formula on the one-layer column, with gusty wind: the big lever, but it needs recalibrating with the rain efficiencies.
   - (C) A flux at a fixed surface humidity: needs a second layer; without one, the prototype rains nothing at 20–40°.
   - **Lean B.**
2. **The vapour's share of the land–sea wind.**
   - (A) All of it.
   - (B) By the ground's wetness.
   - (C) A moist-static-energy monsoon: sound, but the naive prototype collapsed the Congo and India.
   - **Lean B.**
3. **The trigger's reference aloft outside the tropics.**
   - (A) The latitude's sea.
   - (B) The air mass over land and sea. Right for the interiors, but it dries the humid subtropics while their summers are 4–6 °C warm. So it goes in only with that fix (no temporary fixes).
   - **Lean B, with the warm-summer fix in step 3.**
4. **Cost:** accept ~+1 s per warm L7 update and +2–3 s per cold L7 world? **Lean yes.**
5. **Renormalisation.**
   - (A) Keep the 1000 mm global mean.
   - (B) Absolute rain from the bulk E; this needs surface energy budgets the model lacks.
   - **Lean A.**
6. **PW-307:** before (step 0, merged alone), during, or after? **Lean before.**

## References
- Bretherton, Peters & Back 2004, J. Climate 17. Neelin, Peters & Hales 2009, J. Atmos. Sci. 66 (rain and column water).
- Dai & Trenberth 2002, J. Hydrometeorology 3 (river discharge to the oceans).
- Frierson, Held & Zurita-Gotor 2007, J. Atmos. Sci. 64; Hwang & Frierson 2010, Clim. Dyn. 36; Siler, Roe & Armour 2018, J. Climate 31 (diffusive moist energy balance).
- Smith & Barstad 2004, J. Atmos. Sci. 61 (orographic precipitation).
- Talley 2008, Prog. Oceanogr. 78; Baumgartner & Reichel 1975 (fresh-water budgets).
- van der Ent et al. 2010, Water Resour. Res. 46 (recycling).
- Zaucker & Broecker 1992, J. Geophys. Res. 97 (Atlantic vapour export).

Published numbers are rounded, for scale, never targets.
