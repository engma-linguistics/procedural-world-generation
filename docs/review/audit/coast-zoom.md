# Physics audit (PW-245): coast (waves, tides, Galloway) and regional zoom

Auditor: audit-coast-zoom, 2026-10-15. Code: `planet/coast.py`, `planet/zoom.py`, `zoom_kernels.py`,
`zoom_terrain.py`, `zoom_landforms.py`, `zoom_volcanoes.py`. Graded on the owner's axis: **sound
approximation** (a crude but physically based simplification) vs **bandaid** (forces an answer, hides a
process error, or only works on Earth).

Measurements: `coast.galloway` on six Earth deltas with real Q, sediment, waves and tides; an in-memory
L7 zoom (world 592f2a, -9.35/-161.39, 2000 km at 4 km/px, nothing saved), instrumented with a scratch
copy of `zoom.py` that records each coarse cell's mean after each stage. Scripts:
`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/{gw.py,zcheck.py,zstages.py,patch.py}`.

## Findings

### 1. Delta plain radius is 3-5x smaller than its own Earth calibration, so tide-dominated deltas come out river-dominated (med-high; unsound, a bug)
`coast.py:528-533` `plain_radius_km = clip(10 (Q/100)^0.35 (0.8 + 0.6 sf), 15, 300)`. The docstring and
`zoom.py:661` give the calibration: Nile ~150 km at 2,800 m³/s, Mississippi ~250 km at 17,000, G-B
~350 km. The formula gives Nile 26-45 km, Mississippi 48-85, G-B 64-112. It has been like this since it
was written (961b903); the numbers were never checked against the formula.
It matters twice: the delta plain drawn in the zoom is that small (a cause of PW-061's "delta fans are
small"), and the tidal prism grows as R², so the Galloway tide weight is ~10x too small:

| delta (real Q, Qs, wave, tide) | R from formula (sf 0..1) | weights then | at the docstring's R |
|---|---|---|---|
| Ganges-Brahmaputra | 64-112 km | river 0.81-0.61, **river-dominated** | tide 0.86, tide-dominated |
| Mekong | 46-81 km | river 0.78-0.63, **river-dominated** | tide 0.71, tide-dominated |
| Fly | 34-59 km | river 0.60 / tide 0.57 | tide 0.80 |
| Mississippi, Nile, Sao Francisco | | river, river, wave | same types |

The module docstring itself names G-B, Mekong and Fly as the tide-dominated examples.
**Fix:** refit the coefficient to the stated sizes (roughly `40 (Q/1000)^0.35 ...`, so Nile ~120-150 and G-B
~300+), keeping the cap at 300-350 km. **Likely effect:** bigger zoom deltas; more tide- and mixed-type
deltas at big macrotidal mouths; `test_delta_types_differ` thresholds may need to be re-derived (not
loosened). Draft: `draft-audit-coast-zoom-delta-radius.md`.

### 2. Wind recovery off land doubled to fit the enclosed-sea rows (med; bandaid)
`coast.py:129` `LAND_SLOW, L_RECOVER = 0.5, 1200.0`. Commit 4f11406 changed 600 to 1200 km and reported
only the coast_check result ("Gulf of Lion 16.8 -> ~10, Baltic 12.8 -> ~8.5 ... waves within 2x 26 -> 28 of 33").
The physical process it stands for, the marine internal boundary layer, brings an offshore wind up to its
over-water speed within ~10-50 km (the SPM/CEM land-to-water correction applies to fetches of tens of km).
With 1200 km, wind is still ~30% slower 600 km off any upwind coast, so it cuts power over large parts of
every ocean near land, not only in enclosed seas. U_TRADE and U_STORM were not refitted after the change.
Enclosed seas are still ~2x high (PW-075), so the real cause wasn't found. The next finding is one candidate.
**Fix:** put L_RECOVER back to a physical ~50 km (LAND_SLOW ~0.3), and fix the growth law first (finding
3). Then refit U_TRADE/U_STORM once, on the open-ocean rows only. Draft: `draft-audit-coast-zoom-land-wind-recovery.md`.

### 3. The gust factor is derived for U⁵ but applied to U, which over-weights fetch- and duration-limited seas (med; unsound)
`coast.py:124-127, 305`. `GUST = 1.43 = 6.1^(1/5)` is exact for a fully developed sea (P ~ U⁵). But the
code multiplies U by 1.43 before the growth law. In this code's own law, fetch-limited power goes as
U^(7/3) F^(4/3) and duration-limited power (T_STORM 12 h) as U³. For a Weibull k=2 wind the right
factors on power are E[U^(7/3)]/Ū^(7/3) = 1.43 and E[U³]/Ū³ = 1.91. The code gives 1.43^(7/3) = 2.30 and
1.43³ = 2.92. That overstates limited seas by **1.61x** (fetch) and **1.53x** (duration) relative to fully
developed trade-wind seas. Mid-latitude storm seas are duration-limited (u = 15 m/s: 191 km to the duration
limit vs 504 km to full development), so the storm belts are inflated relative to the trades. The
calibration of U_TRADE/U_STORM partly absorbs this, so it doesn't cancel cleanly anywhere.
**Fix:** drop GUST and take the mean of the power over a few Weibull speed quantiles (e.g. 5 nodes) per
season in `_wave_rays`. That costs 5x the ray walk; alternatively apply the moment ratio that matches
the regime of each growth step. Draft: `draft-audit-coast-zoom-gust-moment.md`. Relates PW-074/075.

### 4. Zoom: valley carving lowers each cell's mean by ~60-90 m and nothing restores it; docs say every mean is kept (med; hidden inconsistency)
`zoom.py:1455-1457` (`h = smin(h, T)` after the mean correction at 1118-1123), then the landscape pass
fits C to box means of that carved target (`tmean`, 2094), not to the coarse means. Staged
measurement, land cells not on the coast, zoom of 592f2a (bias / RMS, m):

| stage | land | land > 1500 m | sea interior |
|---|---|---|---|
| detail + mean correction | -0.0 / 93 | -2 / 105 | +397 / 854 |
| volcanoes, landform target | +2.6 / 94 | -1 / 105 | +415 / 912 |
| coarse valleys carved | **-58 / 185** | **-69 / 212** | +415 / 912 |
| landscape pass | -66 / 226 | -72 / 261 | |
| creep + landform remap | -86 / 234 | -96 / 269 | +415 / 912 |

Water is fine (below). Only the "every coarse cell's mean height is kept" claim (overview §2.13, zoom
docstring step 4) is untrue after the carving. `stats.cell_mean_rms_error_m` (516 m here) exists but no
test or doc reads it.
**Fix (simplest sound):** compute `tmean` from the pre-carving surface (or re-apply `keep_means` to land
outside the valley bottoms after carving), so the stream-power fit restores the coarse mean. Draft:
`draft-audit-coast-zoom-cell-means.md`.

### 5. Zoom: narrow deep sea features (trenches) lose up to ~3.5 km of depth (low-med; numerical, not a bandaid)
Trench cells at -7,700 m come out at -3,700 to -5,600 m fine means. Sea-interior bias is +415 m, and it
dominates the zoom's reported RMS. Cause: `e_sea` is a Gaussian (σ = 0.5 cell) average, and the mean
correction (`zoom.py:1118-1123`) is itself a Gaussian-smoothed residual applied twice, which can't
restore a one-cell-wide feature. Folded into the cell-means draft (same fix family: more correction
iterations or a sharper sea kernel near steep coarse relief).

### 6. Tide shelf resonance is held at its peak for every shelf wider than a quarter wavelength (low; bandaid-ish clamp)
`coast.py:441` `cos(np.minimum(kw, pi/2))`: beyond λ/4 the amplification stays at 1/r = 3.3, then only
the friction exponential takes it down. The linear model's response falls back towards 1 near λ/2. The
λ in use is from the coast cell's own (shallow, clipped to 20-150 m) depth, not the shelf's, so λ/4 is
often only ~150-300 km, and many wide shelves sit at full resonance. **Fix:** drop the min (keep the r term,
which already bounds the peak), use the shelf's mean depth for λ. Check Patagonia/NW Australia/Siberia in
coast_check. Draft: `draft-audit-coast-zoom-shelf-resonance.md`. Relates PW-076.

### 7. Zoom coarse lakes: no open-water evaporation, rain counted as land runoff on the lake (low)
`zoom.py:1636, 1881-1889`: `srcq` on lake pixels is the interpolated land runoff, and an open lake passes
`sum(q over its pixels)` on at its outlet. The lake's own net evaporation (as `basin_lakes` does for
landform basins) is never subtracted, so a big open lake's outflow is overstated relative to the coarse
world. Draft: `draft-audit-coast-zoom-lake-evap.md` (relates PW-060).

## Checked and clean (or sound approximations)
- **Wave energy formulae** (`_wsat`, `hs_te`): PM Hs = 0.24 U²/g, Te = 6.75 U/g, P = ρg²Hs²Te/64π = 0.49 Hs²Te
  kW/m; the inverse Te = 4.4 √Hs is consistent. JONSWAP fetch law P ~ F^(4/3), equivalent-fetch
  bookkeeping and the duration limit gF/U² = (gt/68.8U)^1.5 are correct. Directional normalisation
  wk = 4/ndir is right (Σcos² over the downwind half = ndir/4). Sound.
- **Swell decay** 8000 km and **bottom friction** (`exp(-depth/35 m)/250 km`): crude, within the observed
  range (swell e-folding 3,000 to >20,000 km). Sound.
- **Sea-ice share** (sine through warm/cold months) and the hard `icy >= 0.5` ray block (PW-230, known).
- **BQART**: ω = 0.0006, units right; `T >= 2 °C` clamp reproduces BQART's own cold-basin branch exactly.
  B (lithology 0.6-2, glacial ×2) is a reduced form of B = I L (1-TE) Eh. Sound.
- **CERC** Qw = 0.14 Hs^2.4 Te^0.2 m³/s: Ashton & Murray's K1 = 0.34 at the maximum-transport angle. Sound.
- **Tidal flux** Qt = Qs × Q_tide/Q (Nienhuis 2020). Sound.
- **Tide connection**: deep-basin size (BASIN_KM 6000, GATE_KM 100), conductance by depth, screened diffusion.
  It was motivated by the Arctic rows, but it's generic (basin size and sill depth) and continuous across
  the threshold ((6000/5000)² clips to 1). Sound crude proxy, not Earth-keyed. Own tide ~ (size/5000 km)²
  is crude (small-basin equilibrium tides grow ~linearly with size) but harmless.
- **storminess/7**: normalises a °C/1000 km gradient to ~1 in a mid-latitude winter. Sound.
- **Zoom water balance**: in the 592f2a zoom, sea + edge outflow 49.8k m³/s vs runoff on the region's land
  48.9k + 2 entering rivers. Conserved. At each big coarse mouth the fine mouths within 1.5 cells carry
  the coarse discharge (sums 0.9-1.3x). The single biggest fine mouth gets only 40-70% of it (the rest
  goes to parallel coastal streams): part of PW-061, not a new issue.
- **Zoom volcanoes**: edifices, guyots and reef rings follow the run's volcano table (age, planing, living
  reef). Geometry is synthesized, process state comes from the run. Sound. Sea-cell means move +18 m.
- **Landform classes**: explicitly a class-driven synthesis in the docs (not a claimed process). Basin lakes
  are by a real water balance (`basin_lakes`: inflow vs net open-water evaporation × area, closed-lake area
  = inflow / loss). Sound.
- **Glaciers**: the run's `icemass.balance` per pixel; GL_F_MAX/GL_MAX_KM caps are cited to Bering,
  Malaspina, Pio XI. Sound limiters.
- **Tests**: `test_coast` 3e78eaa swapped "tide sea_near > 2× wave" for a mouth-count assertion
  (a different behaviour, not a widened range); `test_volcanoes` f15e7f5 moved the motu/fore-reef radii for
  lobed rims (geometry change, justified); `test_zoom_water` b9a5cea let plunge pools sit below a lake
  outlet (justified). No skipped tests or widened tolerances found in this area.

## Appendix: inventory

Verdicts: S = sound approximation / fine, W = weak (plausible, undocumented), B = bandaid / suspicious.

| file:line | what | justification found | verdict |
|---|---|---|---|
| coast.py:118-119 | U_TRADE 6.5, U_STORM 6.0 m/s | "calibrated on Earth" (coast_check) | W (fit constants; OK once growth law fixed) |
| coast.py:120,121 | N_DIR 24 / 16 | streaks (PW-075) | S |
| coast.py:122-123 | D_MAX 6000, L_SWELL 8000 km | swell literature range | S |
| coast.py:127 | GUST 1.43 on U | Weibull moment of U⁵ | B (finding 3) |
| coast.py:128 | T_STORM 12 h | duration limit | S |
| coast.py:129 | LAND_SLOW 0.5, L_RECOVER 1200 km | doubled to fit coast_check | B (finding 2) |
| coast.py:130 | STORM_ZONAL 0.5 | none | W |
| coast.py:131 | bottom friction 250 km / 35 m | none (plausible) | S |
| coast.py:239 | u > 0.5 m/s threshold | numeric | S |
| coast.py:244,248 | min(fd/fs,1), min(feq/fs,1) | JONSWAP saturation | S |
| coast.py:305 | clip(storm track, 0, 2) | none | W (limiter) |
| coast.py:306,317 | max(sp,1e-6) etc. | numeric guards | S |
| coast.py:347 | icy >= 0.5 blocks rays | PW-230 (known) | B (known) |
| coast.py:348 | depth >= 1 m | numeric | S |
| coast.py:373 | shelf width fallbacks 20h, 0.5h | none | W |
| coast.py:376 | shelf depth clip 20-150 m, coast cell's own depth | none | W (finding 6) |
| coast.py:133 | R_OPEN 2 m | open-coast range | S |
| coast.py:134-135 | D_OPEN 2500 km, OPEN_FRAC 0.55 | none | W |
| coast.py:136-137 | DEEP_M 2000, BASIN_KM 6000, GATE_KM 100 | PW-106 | S (generic) |
| coast.py:138-140 | L_TIDE 3000, CONN_POW 1, H_COND 150 | none | W |
| coast.py:419 | conductance clip 0.02-1 | none | W |
| coast.py:426,433 | own tide (size/5000)², clip 0-1 | none | W |
| coast.py:441 | cos(min(kW, π/2)) | none | B (finding 6) |
| coast.py:142-143 | R_FRIC 0.3, L_SHELF_FRIC 1200 km | none | W |
| coast.py:147 | ICE_FRIC 1.0 | ice-ocean drag ~ bottom drag | S |
| coast.py:444 | funnel (0.5/near)^0.5 clip 0.65-2.2 | Green's law | W (cap undocumented) |
| coast.py:455 | CHANNEL_SHARE 0.002 | none | W |
| coast.py:456 | PLAIN_Z0 0.8, PLAIN_RISE 10 m | matches zoom plain | S |
| coast.py:457 | SED_DENSITY 1600 | 2650 × 0.6 | S |
| coast.py:482 | relief = max(p98 elev, 0.05 km) | robust max | S |
| coast.py:483 | T >= 2 °C | BQART cold branch | S |
| coast.py:486 | B = (0.6+1.4 soft)(1+iced) | reduced BQART B | S |
| coast.py:533 | plain radius 10 (Q/100)^0.35, clip 15-300 | Earth sizes cited, not met | B (finding 1) |
| zoom.py:163 | RUGGED per rock | none | W (style) |
| zoom.py:941-947 | ruggedness 0.65 on cover, boundary floors, clip 0.12-1 | none | W (style) |
| zoom.py:168 | SPL_M 0.5, KD 0.25, MAX_SLOPE 450 m/km, 6 steps | m/n = 0.5 | S |
| zoom.py:169 | DELTA_MIN_Q 1500 | none | W |
| zoom.py:673,675 | n branches / mouths clips | none | W (style) |
| zoom.py:677 | lobe radius 0.22 R | none | W |
| zoom.py:993 | no plain above 250-800 m | none | S |
| zoom.py:1091 | 2.2 tanh(detail/2.2) | "no absurd spikes" | S (limiter) |
| zoom.py:1100-1101 | softplus coast clamp | keeps coast | S |
| zoom.py:1120 | mean correction only cnt > 0.25 px, 2 iterations | none | W (finding 5) |
| zoom.py:1149 | land >= 0.5 m, sea <= -0.5 m | coast consistency | S |
| zoom.py:1257 | valley floor e(1 - 0.12 - 0.33 r) | none | W (finding 4) |
| zoom.py:1455 | smin carve, no mean restore | none | B (finding 4) |
| zoom.py:1385 | falls scaled to 0.85 of drop | fits the reach | S |
| zoom.py:1616,1619 | lake depth scale clip 0.7-3, ell 2 px-80 km | keep coarse mean depth | S |
| zoom.py:1709 | rapids <= 150 km | none | W |
| zoom.py:1717 | rapids floor <= coarse ground | consistency | S |
| zoom.py:2099 | cap = tmean + min(1.8 amp, 3000) | summits | W |
| zoom.py:2145 | C update clip 0.5-2, ^0.8 | stability limiter | S |
| zoom.py:2196-2198 | final max 0.5 / rims / outflow caps | consistency | S |
| zoom.py:2277,2302 | plunge pool 0.6 h, 3-60 m | Niagara | S |
| zoom.py:383-401 | COAST_FLOOR_GRAD, RAPIDS_GRAD, BANK_*, SETTLE_M, ICE_SNOUT_GRAD... | design limits, each commented | S |
| zoom.py:379-380 | KP_* knickpoint thresholds | commented | S |
| zoom.py:262-265 | WF_* fall detection | commented | S |
| zoom.py:395-401 | LF_LAKE_*, LF_LOSS_MM 300, BARRIER_*, MARSH_* | fallback / style | W |
| zoom.py:828-833 | GL_* tongue widths and caps | Franz Josef, Bering, Pio XI | S |
| zoom.py:885 | ice thickness clip 20 m-ICE_MAX | none | S |
| zoom.py:1636 | lake pixels get land runoff, no lake evap | none | B-low (finding 7) |
| zoom_volcanoes.py:42,61,142,159-177 | motu share, shore limit, lobe/wobble clips, reef depths | style | S |
| zoom_landforms.py:173 | RESIST per rock | lip strength | S |
| zoom_landforms.py:289-290, 595-596 | patch lattice, zone relief 0.36 e + 25 | matches zoom detail | S |
| zoom_landforms.py:726-730 | gap/gorge sizes, GORGE_KM √(Q/1000) | Niagara-type retreat | S |
| zoom_landforms.py:1372-1378, 1448 | relief, karst, pond, face, playa constants | style | S |
| zoom_landforms.py:1503-1526 | basin water balance | PW-167 | S |

Counts: 67 items: **S 38, W 22, B 7** (findings 1-4, 6, 7, and the known PW-230 block).
