# Physics audit (PW-245): climate and ocean

Scope: `planet/climate.py`, `planet/ocean.py`, and where the run calls them (`tectonics/earth.py`: `update_climate`, and `global_temperature`, which sets the `dT` the climate gets). Read against `docs/overview.md` §2.6–2.7. I measured on the showcase run a1d3b9 (seed 3199, L7, 1000 Myr), last frame averaged onto L6, with `climate.compute` at dT = 0 and no vegetation feedback. Scratch scripts are outside the repo; nothing under `planet/` or `tests/` was changed.

**Overall:** no Earth-specific or region-specific branches. The code has no longitude tests, no basin or continent ids, and no coordinate boxes. Every latitude dependence is a smooth ramp tied to a named process (Hadley/Ferrel belts, Coriolis fading at the equator, polar ramps). Earth shows up as calibration anchors: the latitude temperature curves are fitted to Earth, and the vegetation feedbacks are referenced to Earth's land means so that Earth stays neutral. That is a legitimate way to parameterize a diagnostic model, and it is documented. I found two real conservation leaks, one design choice that weakens the thermostat, and one trivial bug.

## Findings

Graded on the owner's axis (2026-10-15): a **sound approximation** is a recognised simplification with a physical basis, however crude; a **bandaid** forces an answer, hides a process error, or only works on Earth. Finding 1 is a bandaid: it was kept for a metric and double-counts heat. Finding 2 is a process inconsistency that a bandaid hides (the freshwater mean). Findings 3 and 4 are a design choice and a slip. Everything else I inventoried as sound approximations or weakly justified constants (see the appendix), not bandaids.

### 1. Overturning heat is added with nothing taken away, and was kept because the Köppen score preferred it (high)
- **Where:** `climate.py:822-826` (`sea_surface`, `share` branch), `ocean.py:588-592` (`solve.sst_c`), `TUNE["moc_zonal"] = 0.0` (`climate.py:1377`).
- **What:** the inflow's warmth `E` is added to the SST, and `moc_zonal × zonal_mean(E)` is subtracted from it. The default `moc_zonal` is 0, so nothing is subtracted. The heat the inflow carries is also never taken from the low latitudes it comes from (`_along` only relaxes the inflow toward `t_eq`). So the overturning is a net heat source for the sea surface. The code's own comment gives the reason this is a double count: "t_eq was fitted to Earth's sea, overturning and all". The wind-driven gyres, by contrast, conserve heat within each band (`sea_surface` removes each band's mean anomaly).
- **Why suspicious:** commit d909b83's notes say the value was picked on the metric: "The Köppen score preferred this (70.69% against 70.50% with half of it taken off the band)". A 0.19-point Köppen gain was bought with a heat source that has no physical basis.
- **Evidence (a1d3b9 at L6):**

  | moc_zonal | Ocean-mean SST warming | Poleward of 45° | Global mean T |
  |---|---|---|---|
  | 0 (default) | +0.52 °C | +0.98 °C | 14.41 °C |
  | 0.5 | +0.26 °C | +0.50 °C | 14.22 °C |
  | 1 | +0.02 °C | +0.06 °C | 14.04 °C |

  The local maximum is +7.6 °C. Land poleward of 50° is 0.29 °C colder at `moc_zonal` = 1. The sinking sites are unchanged at ~16 Sv each, so the circulation itself doesn't depend on this term.
- **Proper fix:** take the transported heat out of where it comes from, so that ∑ area × ΔSST ≈ 0. Either cool the source band (equatorward of `moc_src_lat`) and the route by what the inflow gives up, or at least use `moc_zonal` = 1 so the warming stays within its band. If `t_eq` is meant to stand for "Earth with its AMOC", the sinking latitudes should be cooled by the mean overturning warming, and the model then adds back only the deviation from it.
- **Likely effect:** high-latitude seas 0.5–1 °C cooler on average where no strong inflow reaches (the North Pacific analogue); global T −0.3 to −0.4 °C at dT = 0, which can be re-centred with the curve offsets. This may also bear on PW-038 (NE Canada and Labrador too warm). Draft: `draft-audit-climate-ocean-moc-heat-not-conserved.md` (needs-decision).

### 2. The rain model's land evaporation is not the water balance's, and the gap is hidden by subtracting the freshwater mean (med)
- **Where:** `_rain` land recycling, `m += et × warm × year/S` (`climate.py:930-934`); `water_balance` (Budyko AET); `ocean.freshwater` subtracts the global mean (`ocean.py:470-472`); `compute` line 1838 zeroes sea evaporation under sea ice after the kernel has already used it.
- **What:** the atmosphere's water and the surface's water are two separate budgets.
  - The kernel's land source is `et` (0.5) × `warm` × the local rain, which works out to 41% of land rain globally.
  - The land's own budget (Budyko) evaporates 60%.
  - The kernel also takes up vapour over sea ice that the freshwater budget then removes.
  - Whatever doesn't close is taken off as a uniform freshwater mean.
- **Evidence (L6, km³/yr):**
  - The kernel takes up 444,700 over the sea, of which 13,800 is under sea ice. It recycles 65,800 from land, while Budyko's land AET is 95,400.
  - Net to the sea: P_sea − E_sea + runoff = −16,800 (−4.7 cm/yr), which `freshwater` removes as `mean = −0.0475 m/yr`.
  - With `et` = 0.73, land rain rises 22% and the mean flips to +0.074, so the budget closes somewhere near et ≈ 0.55–0.6.
- **Why it matters:** salt and freshwater are conserved only by renormalising. The interiors get less recycled moisture than the land actually evaporates. This is a candidate cause for part of PW-026 (maritime air not reaching inland) and of PW-228 (regional rain), and it is the deficiency `vapour_mixed` patches for humidity (its docstring: "the rain model's air loses its water too readily over long dry stretches"). It relates to PW-013.
- **Proper fix:** feed the kernel the water balance's own evaporation: the per-cell AET/P from the first-pass temperatures, or a fixed-point iteration of the two. Also give the kernel the sea-ice open share (`open_y`) so the air takes up nothing through ice. Then the freshwater mean should come out near 0 by itself, and can become an assertion instead of a correction.
- **Likely effect:** land rain +5–10% (more inland), slightly less sea rain after the global normalisation. The Earth checks will move, so re-run `earth_check` and the vegetation check. Draft: `draft-audit-climate-ocean-rain-recycling-vs-budyko.md`.

### 3. The weathering thermostat compares rates, not a CO2 stock, so a lasting change in degassing is forgotten in ~200 Myr (low, judgement call; a sound approximation, not a bandaid)
- **Where:** `tectonics/earth.py:64-87, 120`.
- **What:**
  - `co2 = log(source/source_ref) − log(sink/sink_ref)`, and both references learn toward the current rates with a ~200 Myr time constant.
  - A permanent doubling of degassing gives about +1.5 °C at first (the feedback of `WEATHER_K` = 0.12 on 3 °C per unit). That decays to 0 as the references catch up.
  - In the real carbonate–silicate cycle, CO2 is a stock: it builds until weathering matches degassing, a permanent +5.8 °C for exp(0.12 ΔT) = 2.
  - The index is also hard-clipped at ±1.5 (±4.5 °C).
- **Why suspicious:** it isn't metric-chasing; it is documented ("only changes count") and keeps runs near Earth's temperature. But it means the "thermostat" only damps transients. Long-term temperature is set by `drift`, not by the balance between tectonic degassing and weathering.
- **Options:** (A) keep it as is and say so in the docs; (B) integrate a CO2 stock, d ln CO2/dt ∝ source − sink(T), with the weathering law as the only restoring force; (C) as now, but with references that learn much more slowly (≥1 Gyr). **Lean: C**, the simplest change: it keeps the current design and lets sustained forcing last. B is the textbook form, but it is heavier and would need retuning. This is not metric-chasing; it is a design simplification with a physical basis. Draft: `draft-audit-climate-ocean-co2-rate-not-stock.md` (needs-decision).

### 4. The kernel's evaporative cooling estimates rain in mm without the warm-world factor (low, xs)
- **Where:** `climate.py:906`, `scale = mean_mm × S × n / tot`. `compute` normalises the rain to `mean_mm × exp(0.03 dT)` (line 1832), but `rain()` passes the bare `tune["mean_mm"]`.
- **Effect:** at dT = ±10 the kernel's mm estimate is off by ×1.35, which shifts the shower instability by up to ~0.3 °C. Negligible near dT = 0. Fix: pass `mean_mm × exp(0.03 dT)` (for example through `tune`). Draft: `draft-audit-climate-ocean-tcor-wet-scale.md`.

### Looked suspicious, turned out justified or already tracked
- **Ice surface cooling** (`ice_cover`'s 15→50° ramp; `ice_cooling` 10 °C). Its docstring admits the ramp also compensates for "the model's sea-level summers, calibrated on ice-free land, are too warm for an ice surface". That is the same root as **PW-112** (bare polar summers too warm) and **PW-039**: the latitude curve has no albedo or snow term for bare polar ground, and the 10 °C stands in for it on ice. I'm not filing it again. Fixing PW-112 properly should let the ramp and part of the 10 °C go.
- **Coldest-month test bound loosened from −95 to −110 °C** (`tests/test_invariants.py:51`, 1a2b851). Tracked as **PW-226**: the cause is the 9.5 km ice surface, not the climate. The climate applies a linear lapse rate (−62 °C at 9.5 km) on top of the −10 °C ice cooling. That is correct for its inputs.
- **Earth Köppen test**: `agree >= 0.66` became `>= 66` (4fffb92). That is a units change (fraction to %), not a loosening.
- **Global rain renormalisation** (`mean_mm`, 3%/°C) and the 8000 mm/yr clip are documented. The clip hits 79 of 40,962 cells at L6 (0.19%), so it acts as a backstop, not a process.
- **Units checked:**
  - The Roquet 2015 equation of state: coefficients and the sign of the thermobaric term match the paper.
  - Thermal wind, u = gH/(fT)·∇T: k is m/s per °C/km, correct.
  - Lebedev's sea-ice law and Oudin PET (which uses Ra, as Oudin defines it) are right.
  - Köppen thresholds match Peel 2007 (C/D at −3 °C, as `earth_check` documents).
  - The Stommel solve is consistent in nondimensional β.
- **Salt** is conserved exactly: the freshwater mean is removed, and the salinity area-mean is pinned to S0 (fine, though see finding 2 for what that mean hides).
- **The gyres** conserve heat per latitude band. Upwelling cold is redistributed within its band, which is plausible.
- **No double counting** between the kernel's rain-based `tcor` and `_land_finish`'s evaporative cooling: one sets shower instability, the other the output temperatures.
- **Brine** counted in both the annual freshwater (exported ice) and the winter density pulse: at most a ×2 overcount on the exported share. Plausible size, left alone.

## Appendix: inventory

Verdicts: **sound** (a sound approximation: physically grounded, or a documented numerical-stability backstop), **weak** (a sound approximation, but the constant is tuned or unexplained), **bandaid / suspicious** (forces an answer or hides an error; see findings). Every "fine" below means sound.

| file:line | what | justification found | verdict |
|---|---|---|---|
| climate.py:50-60 | land temperature polynomial in sin²(lat), fitted to Earth | docstring; overview §2.6 | fine (Earth calibration anchor) |
| climate.py:63-70 | sea curve, \|sin\|^2.3 exponent | docstring (Earth SST values) | fine |
| climate.py:1775 | `tilt_adj = (tilt−23.4)·0.3` | one-line comment only | weak |
| climate.py:1776 | eq +0.5·dT, pole +1.5·dT (polar amplification ×3) | overview | fine |
| climate.py:1779 | sea curve offsets eq −0.8, pole +2.9 | none | weak |
| climate.py:81 | season damping `clip(0.65 + a/70)` near the equator | docstring (weak Coriolis) | weak |
| climate.py:94-96 | continental swing 4+24·(1−e^(−d/800)), +0.3 on land | docstring (Vancouver/Yakutsk) | fine |
| climate.py:483-506 | wind belt Gaussians (12°, 48°, 78°), `TRADE_ROUND` 3° | docstring, PW-227 | fine |
| climate.py:534-541 | monsoon: Coriolis ramp to 15°, 0.3 gain, cap 0.7·clip((65−lat)/25, 0.3, 1) | comment ("shallow, never overrides belts") | weak (hard cap) |
| climate.py:549-573 | orographic deflection, block_m 1500, speed kept, ≤1/0.3 boost | docstring | fine |
| climate.py:709 | gyre boundary width ≥ 0.8 cell | comment (resolution) | fine |
| climate.py:712 | Stommel damping r/3000² | docstring (well-posed) | fine |
| climate.py:741 | currents soft-capped at 2.5 m/s (tanh) | comment; 0.08% of sea cells > 2.0 | fine |
| climate.py:735-738 | no flow into coasts within 2 cells | comment | fine |
| climate.py:795-796 | Ekman offshore clip 1.5; coastal upwelling only at 5–45° | none for the bounds | weak |
| climate.py:813-817 | equatorial upwelling only where land is to the east | comment (thin warm layer) | fine |
| climate.py:829-832 | gyre SST anomaly band-mean removed | docstring | fine (conservative) |
| climate.py:822-826, 1377 | `moc_zonal` = 0: overturning heat not removed anywhere | commit d909b83 (Köppen +0.19 pt) | **suspicious** (finding 1) |
| climate.py:854, 859 | humidity floor `HUMID_MIN` 0.15 | docstring; 0% of land cells at the floor in this world | fine |
| climate.py:962-978 | `vapour_mixed` background vapour (diagnostics only) | docstring (PW-151): patch for a kernel deficiency | weak (finding 2's symptom) |
| climate.py:906-911 | kernel evaporative-cooling `scale` without the wet factor | none | **suspicious** (finding 4, trivial) |
| climate.py:930-934 | land recycling `et`·`warm`·rain, not tied to Budyko | TUNE comment | **suspicious** (finding 2) |
| climate.py:943 | shower instability capped at 2 | none | fine (rate saturation) |
| climate.py:1181 | eddy diffusion clip 0.12 + B, ≤1 | none | fine |
| climate.py:1187-1189 | large-scale rain floor 0.05; −0.3 polar dry | comment | fine |
| climate.py:1199-1200 | weak temperature gradient: tropics' aloft temperature to wtg+15° | comment | fine |
| climate.py:1205 | air movement floor 0.25 | none | weak |
| climate.py:1206 | recycling needs warmth, clip(t/15) | comment | fine |
| climate.py:1832-1834 | rain renormalised to 1000·e^(0.03 dT); clip 0..8000 | overview (documented) | fine (79 cells at the clip) |
| climate.py:1838 | sea evaporation × open share (the kernel didn't know) | comment | weak (finding 2) |
| climate.py:1853 | sea-ice growth (0.2 + 0.8·clip(open/0.25)) | comment (thick ice insulates) | weak |
| climate.py:1862 | perennial-ice index clip(1 − 2·open) | none | weak |
| climate.py:1873 | sea seasonal swing damped near freezing, clip 0.1..1 | comment | fine |
| climate.py:1932-1935 | air over sea ice 3× (and 1.5× more in winter) the "below freezing" of the latitude curve | none | weak (unexplained factors) |
| climate.py:1959 | Budyko w clip 1.5..4 | none (standard Fu range) | fine |
| climate.py:1961 | recycling vegetation band ±0.2 | docstring (stops runaway) | fine |
| climate.py:1985 | albedo warming capped ±2 °C | TUNE | weak |
| TUNE `veg_w_ref`, `et_lai`, `albedo_ref`, `albedo_snow_ref` | Earth land means as references | comments ("so Earth stays") | fine (anchors, not branches) |
| climate.py:2032 | ice cooling only poleward of 15→50° | docstring admits it compensates for too-warm summers | bandaid-leaning (tracked: PW-112) |
| climate.py:2047-2064 | ice surface: −10 °C·cover, positive summers halved | docstring | weak (PW-039/112) |
| climate.py:1014, 1021 | cloud polar ramp 60→80°, storminess clip 1.2 | docstring | fine |
| TUNE cloud_* (~20) | cloud parameters | docstring per kind; PW-162/232 | fine (diagnostic, no feedback, PW-163) |
| climate.py:1064-1070 | sunshine 0.95 − 0.9·cloud | docstring (recorder threshold) | fine |
| ocean.py:82-91 | Roquet SEOS coefficients | paper | fine |
| ocean.py:79 | `ICE_FRESH` 0.72 | comment | fine |
| ocean.py:205-212 | Lebedev 1.33·FDD^0.58 | paper | fine |
| ocean.py:286 | dilution per step ≤ 0.5 | none | fine (stability) |
| ocean.py:334 | inflow cost clipped e^±2 | comment | fine |
| ocean.py:360 | sinking gate ((excess)/drho)^3 | TUNE | weak |
| ocean.py:373-379 | per-sea cap `moc_k` | docstring (Wright & Stocker) | fine |
| ocean.py:586-610 | spin-up `moc_spin` 6× | docstring | weak (known PW-016/PW-022) |
| ocean.py:415 | inflow share ramps in 10° past `moc_src_lat` | comment | fine |
| ocean.py:450, 627 | salinity mean pinned to S0 | docstring (salt conserved) | fine |
| ocean.py:470-472 | freshwater mean removed | docstring | weak (hides finding 2's gap) |
| ocean.py:633 | fine-grid sinking rescaled to the coarse total | comment | fine |
| ocean.py:643-657 | `LOOP_*` (viewer schematic only) | comments | fine (cosmetic) |
| earth.py:25 | `WEATHER_K` 0.12 | GEOCARB comment | fine |
| earth.py:84-85 | references learn over ≤200 Myr | docstring | **suspicious** (finding 3) |
| earth.py:120 | CO2 index clip ±1.5 | none | weak (finding 3) |
| earth.py:115-120 | ice albedo tanh cap at 3 °C, relative to Earth's 3.1% ice | comment (PW-190) | fine |

Counts: 61 items, of which 35 sound, 21 weak (sound but tuned/unexplained) and 5 suspicious, the bandaids among them being `moc_zonal` = 0 and the freshwater-mean correction. Two items lean bandaid but are already tracked: the ice-cooling latitude ramp, which compensates for too-warm polar summers (PW-112), and the 3× air-over-sea-ice factor, which is undocumented. The run's code tolerates no Earth geography beyond the latitude-curve calibration.
