# Coast batch (2026-10-16): PW-230, PW-075, PW-297, PW-323

One commit per ticket. World-level only (planet/coast.py, planet/coastal.py); no run changes. Measured with `tools/coast_check.py` (Earth, L6 unless marked, the model's coupled climate, cached once so every column uses the same climate) and `tools/coastal_check.py` (the Earth world built in memory). "Before" is main at 6392e18, whose climate differs a little from fixes-coast-zoom.md's: waves within 2× are 25/33 here, 24/33 there.

| ticket | outcome |
|---|---|
| PW-230 Laptev / Kara no waves | mechanism fixed; the rows stay at 0 because the climate never thaws their coast cells (draft for the climate) |
| PW-075 enclosed seas, India W | stopped: the cause is the wave-driving wind; needs a decision (draft) |
| PW-297 macrotidal shelves | fixed: the sloping shelf's standing wave (J0) instead of the flat shelf's (cos) |
| PW-323 turbidity from resuspension | fixed: bed stress of tides and waves stirs up the floor's mud |

## Summary: coast_check (Earth L6)

| | before | after PW-230 | after PW-297 | final |
|---|---|---|---|---|
| waves in range / within 2× (of 33) | 4 / 25 | 5 / 25 | 5 / 25 | 5 / 25 |
| tides in range / within 2× (of 26) | 12 / 22 | 12 / 22 | 16 / 24 | 16 / 24 |

(Hawaii has no coastal cell at L6, so 32 wave and 25 tide rows are scored; the denominators are the tool's.)

## PW-230: waves from a frozen sea's open season

**Was:** a ray stopped at any cell frozen for at least half of the half-year (`icy >= 0.5`), and the power arriving was scaled by the coast cell's open share. A sea open three months of a mostly frozen half-year made no waves at all; a sea 49% frozen blocked nothing.

**Now:** coast.sea_ice_share's sine gives every cell an open window centred on the same warm peak, so the windows nest. At a moment a share x into the coast cell's open time (x uniform on [0, open share]), the open sea is exactly the cells open longer than x. The half-year's power is the integral over those moments, each with the frozen sea stopping the waves like land: 3-point Gauss-Legendre (`ICE_QX`, `ICE_QW`). Rays with no ice along them while the coast is open are grown once. Earth L6 wave_power 4.1 → 5.6 s.

**Laptev and Kara stay at 0.0 kW/m, and the rays aren't why.** Their coast cells are frozen all year. The climate's warmest month there is −2.1 °C (Laptev, observed 4.9) and −3.1 °C (Kara, observed 2.5), below `climate.FREEZE` (−1.8). Over all 239 coastal sea cells at 66–78° N the model's warmest month has a median of −1.2 °C against 2.7 observed, and 47% never thaw. With +3 °C on the Arctic sea cells' warmest month as a diagnostic (not committed), Laptev gets 5.4 and Kara 4.5 kW/m (observed 0.3–3). The fix belongs to the climate (other agents own climate.py): draft `draft-arctic-coastal-sea-summers-too-cold.md`.

| row (kW/m) | observed | before | after |
|---|---|---|---|
| Laptev (Lena delta) | 0.3–3 | 0.0 | 0.0 |
| Kara (Ob/Yenisei) | 0.3–3 | 0.0 | 0.0 |
| Beaufort (Mackenzie) | 0.5–4 | 6.8 | 7.3 |
| New Zealand SW | 60–100 | 59.9 | 61.0 (now in range) |
| largest other change | | | Cape Town 20.6 → 21.7 |

Test: `test_wave_short_open_season` (a sea frozen 70% of the time everywhere gets 0.30 of the open sea's waves; the old rule gave 0).

## PW-075: enclosed seas too strong, India W too weak (stopped)

India W is the climate's weak July monsoon wind (PW-233, unchanged). For the enclosed seas, per-direction ray contributions show 100–600 km fetches bringing 1–6 kW/m each, because the wind along them is 11–13 m/s. Below, the model's wave-driving wind (U_TRADE |wind| + U_STORM storminess, mean over the sea within 500 km) is compared with rough climatological 10 m winds (ERA5 / QuikSCAT maps, read off by eye: ±1 m/s).

| | model U / observed wind |
|---|---|
| Mediterranean (Nile, Gulf of Lion) | 1.65, 1.60 |
| Baltic, North Sea S, Black Sea | 1.79, 1.62, 2.02 |
| NH open coasts (Ireland, Portugal, Oregon, British Columbia, Hatteras, Japan E) | 1.35, 1.66, 1.77, 1.70, 1.53, 1.42 |
| SH open coasts (SW Australia, Cape Town, S Chile, Tasmania) | 0.99, 1.04, 1.19, 1.08 |

The open-coast calibration splits a NH/SH storm asymmetry (PW-074): NH open coasts end up ~1.5× too strong and SH ones ~0.55×. The enclosed seas are all in the NH and fetch-limited (power ~U^(7/3)). They take the NH excess and add their own, because storms keep their open-ocean strength behind land.

Sound coast-side constants don't fix it. Each row is refitted on the 18 open-ocean rows (U_TRADE, U_STORM on a 1 m/s grid), rms and bias of log(model / middle of the observed range):

| | open rms / bias | enclosed rms / bias |
|---|---|---|
| now (T_STORM 12 h, L_RECOVER 50 km) | 0.53 / −0.01 | 1.61 / +1.47 |
| L_RECOVER 100 km (the boundary layer's inertial length U/f) | 0.53 / −0.04 | 1.55 / +1.40 |
| L_RECOVER 200 km | 0.54 / −0.04 | 1.44 / +1.29 |
| T_STORM 24 h | 0.69 / +0.04 | 1.28 / +0.98 |
| T_STORM 36 h | 0.83 / +0.17 | 1.24 / +0.96 |

The options (a storm-wind reduction behind land in coast.py with a new length; a surface wind from the climate, with PW-074; accept) are in draft `draft-wave-storm-winds-over-land-locked-seas.md` (needs-decision). The lean is the climate, since a coast-side reduction would be a stopgap. No code change.

## PW-297: tides on a sloping shelf

**Cause.** PW-273's response, 1 / sqrt(cos²(kW) + r²) on the shelf's mean depth, is a flat shelf's standing wave. Past the quarter-wave resonance it swings back to 1 by half a wavelength. Most low macrotidal rows sit just there: kW = 2.1–2.3 at Patagonia, Khambhat, St Malo and the Amazon, 4.25 in the Yellow Sea. A real shelf deepens toward the break, and on a uniformly sloping shelf the standing wave is J0(2ω√(x/(g s))) (Lamb 1932, *Hydrodynamics* §186). The wave shoals into the shallowing water as it resonates (Green's law), so past resonance |J0| stays ≤ 0.4 instead of coming back to 1.

**Now:** amplification 1 / sqrt(J0(z)² + r²), z = 2ωW / sqrt(g h_break), with h_break = 2 × the path's mean depth (a uniform slope from the coastline), so z = √2 kW. Resonance is at J0's first zero, z = 2.405, i.e. W = 1.08 λ/4. R_FRIC and the friction decay over extra width are unchanged; the decay now starts at the J0 resonance instead of λ/4. No new tuned constants (`bessel_j0`: power series below 12, asymptotic form above; error < 2e-4, test against tabulated values).

**The ticket's questions.** (1) L7: resolving the shelves alone doesn't recover them. The flat-shelf response gives 12 / 22 of 26 at L7 too, the J0 response 15 / 26. (2) Mean depth along the path vs the deepest route: not changed. The sloping-shelf reading treats the mean depth as half the break depth, which is what the path mean of a uniform slope is. (3) Does exp(−(W − W_res)/L_SHELF_FRIC) double-count r? Only slightly. r caps the peak (damping at resonance), and the exponential is the extra friction over shelf beyond resonance, where r matters little because |J0| ≥ ~0.3 there. A complex-wavenumber friction would merge the two into one term with a depth-dependent drag; that's a bigger change than this ticket.

| tide (m) | observed | before | after (L6) | before (L7) | after (L7) |
|---|---|---|---|---|---|
| Patagonia (San Julián) | 6–11 | 2.17 | 3.66 | 5.84 | 5.52 |
| Gulf of Khambhat | 6–11 | 4.18 | **6.50** | 2.54 | 4.98 |
| English Channel / St Malo | 5–12 | 3.25 | **5.15** | 8.27 | 9.21 |
| Severn / Bristol Channel | 6–13 | 5.87 | **7.71** | 3.89 | **6.67** |
| Yellow Sea (Incheon) | 4–9 | 1.36 | 2.20 | 0.98 | 2.65 |
| Amazon mouth | 3–6 | 2.10 | **3.48** | 1.42 | **3.77** |
| NW Australia (King Sound) | 6–11 | 4.76 | 4.30 | 3.98 | 3.62 |
| Bay of Bengal head | 3–6 | 3.81 | 3.53 | 2.05 | 2.04 |
| Fly mouth | 3–5 | 3.79 | 5.35 (over) | 4.06 | 3.83 |
| Mekong mouth | 2–4 | 1.60 | 1.95 | 0.77 | 1.10 |
| East Siberian (Kolyma) | 0.1–0.4 | 0.07 | **0.13** | 0.05 | 0.09 |
| Baltic | 0–0.2 | 0.05 | 0.09 | 0.02 | 0.05 |
| in range / within 2× | | 12 / 22 (of 25) | **16 / 24** | 12 / 22 (of 26) | **15 / 26** |

Bold: moved into range. Narrow-shelf and enclosed rows are unchanged (z ≈ 0). Patagonia and the Yellow Sea are still low (within 2× now). Patagonia's L6 shelf is 517 km against ~430 real, and the Yellow Sea's connection is 0.47 (a basin resonance this proxy has no term for, PW-076). Drops: King Sound 4.76 → 4.30 and the Bay of Bengal 3.81 → 3.53 (both short of resonance, where J0 rises more slowly than cos); Fly now 5.35, over its 3–5. Deltas: the Amazon becomes tide-dominated (as usually filed; was river), and Fly falls just under the line (tide weight 0.51 → 0.50, "mixed tide-wave").

## PW-323: turbidity from resuspension

**Was:** turbidity came from river mud only, so shallow tidal shelves without big rivers were clear (Wadden Sea 0.6 mg/L, with 22.5% seagrass in its cell).

**Now** (`coastal.bed_stress`, `soft_floor`, `resuspension`; `turbidity` = river mud + resuspension):
- **bed stress** at the cell's mean depth h. Tidal current from continuity: the water landward of a point fills and empties through it, u = a ω x / h, at most a progressive wave's a √(g/h). Here x is the distance from the coastline (half a cell for a coastal cell) and a half the tidal range. Quadratic drag C_d 0.0025. The waves' orbital velocity at the bed, π Hs / (T sinh kh), uses Eckart's dispersion approximation, Hs capped at 0.5 h and friction factor f_w 0.02 (Soulsby 1997);
- above TAU_CRIT = 0.2 Pa (loose fresh mud, ~0.1–0.2 Pa; Winterwerp & van Kesteren 2004), a share 1 − τ_c/τ of the bed's mobile mud MUD_MOBILE = 0.5 kg/m² (the fluff layer, ~0.1–1 kg/m²; Jago et al. 2002) is held through the water column: SSC = MUD_MOBILE × mud × share / h;
- **mud supply** (0..1): the larger of the river mud already there (coastal.MUD's 1–10 mg/L ramp) and the floor's own soft fine sediment (sediment cover 0.1–1 km, not on hard or carbonate rock, not on sandstone).

Turbidity at named seas (Earth L6; observed ranges are rough literature values):

| | rivers only (before) | with resuspension | observed |
|---|---|---|---|
| Wadden Sea | 0.6 | 99.9 | ~20–200 |
| Yellow Sea (Jiangsu) | 4.6 | 58.8 | ~100–1000 |
| Yellow Sea (Incheon) | 0.8 | 33.1 | ~10–100 |
| Gulf of Thailand (inner) | 7.2 | 66.1 | ~10–50 |
| North Sea S | 0.7 | 14.7 | ~10–50 |
| Amazon shelf | 99.3 | 170.0 | ~100–1000 |
| GBR, Bahamas, Red Sea, Norway, Monterey | 0.5–0.8 | unchanged | ≲1–5 |

Coastal sea cells above 10 mg/L: 1.9% → 12.6% on Earth; sea median 0.5 mg/L either way, 99th percentile 1.7 → 14.5. The Persian Gulf (50) and Torres Strait (99) come out high (5–9 m mean-depth cells with 1–2 m tides; observed more like 5–30).

**coastal_check (Earth L6).** "Before" is main; "PW-297 only" is resuspension off (MUD_MOBILE = 0), which separates the tides' effect on the intertidal zone.

| habitat (km²) | observed | before | PW-297 only | final |
|---|---|---|---|---|
| coral reef | 250,000–285,000 | 466,133 | 466,133 | **122,728** |
| mangrove | 130,000–140,000 | 33,870 | 40,743 | 60,032 |
| salt marsh | 55,000–220,000 | 28,341 | 31,392 | 43,657 |
| kelp | 1.5–2 million | 850,556 | 850,556 | 597,827 |
| seagrass | 160,000–600,000 | 1,024,176 | 1,017,340 | **309,535** |
| places as observed (of 55) | | 39 | 39 | **40** |

After merging main (PW-236's HydroSHEDS rivers in the Earth world): reef 129,564, mangrove 59,683, salt marsh 43,508, kelp 596,258, seagrass 324,378 km²; places 39 of 55, because the new Ganges mouth has a false reef again (1.8%).

Per habitat, final before the merge (and main before the batch): reef 8/13 (7; the Ganges mouth loses its false reefs), mangrove 13/14 (12; Guinea-Bissau now present), salt marsh 6/9 (6; Essex now present, the Sundarbans now a false positive), kelp 7/11 (7), seagrass 6/8 (7). The Wadden Sea's seagrass falls 22.5% → 0.5%; observed is a few % of Zostera beds, and the site test's 1% threshold now misses it. Shark Bay 20.7 → 4.8%, Florida Bay 23.9 → 2.3%, Torres 53.5 → 3.3%, Persian Gulf 41.7 → 7.6% (all still present).

**The reef drop is mostly Earth's rock map.** `tools/earth_world.earth_rock` makes every shelf 2 km of shale, so every warm shelf has a muddy floor. GBR 53,000 → 7,000 km² (its reef cells at a median 18 mg/L), Arafura 66,000 → 8,000, Indonesia and the Philippines 179,000 → 55,000. Real warm shelves away from rivers are carbonate sand. Diagnostic (not committed): with limestone on Earth's warm shelves by the run's own carbonate rule (annual SST ≥ reef_temp, river turbidity < 3 mg/L, above −1500 m), reef is 404,000 km² and seagrass 744,000. Draft `draft-earth-rock-map-carbonate-shelves.md`. Kelp's drop (−30%) is cold muddy shelves losing light and rockiness; the 11 kelp sites are unchanged.

**A generated world** (scratch L6 run, seed 11, 600 Myr, sliced at its representative 516 Myr with main's code and with this branch; same terrain, replay matched; not kept):

| | main | branch |
|---|---|---|
| coastal-sea wave power p10 / 50 / 90 / max (kW/m) | 4.5 / 12.9 / 38.0 / 72.1 | 4.7 / 12.9 / 38.0 / 72.3 |
| coastal-sea tidal range p10 / 50 / 90 / max (m) | 0.94 / 1.74 / 2.20 / 6.1 | 0.94 / 1.74 / 2.20 / 5.7 |
| coastal-sea turbidity p50 / p90 / max (mg/L) | 0.7 / 2.2 / 78 | 0.7 / 3.4 / 251 |
| coastal sea above 10 mg/L | 1.6% | 5.4% |
| reef / mangrove / salt marsh / kelp / seagrass (thousand km²) | 414 / 243 / 79 / 197 / 688 | 288 / 271 / 85 / 179 / 477 |

No NaN or negative values, nothing on land. The reef lost (126,000 km² in 59 cells) is on very shallow floors (median 5 m) with ~2.5 m tides, mostly shale: turbid tidal flats. A first version counted sandstone floors as mud too (reef 228,000); sand is too coarse to make a fluff layer, so it's excluded.

Tests: `test_resuspension_on_shallow_tidal_shelves` (a 10 m muddy shelf with a 6 m tide is turbid and loses most of its seagrass; calm water, a hard floor or 150 m of water stays much clearer). `coast_world`'s shelf is now limestone (a reef shelf); on shale its 25 m, 2.7 m-tide shelf is turbid, as the Gulf of Papua's is, and grew no reef.

## Goldens

Unchanged: `tests/test_golden.py` passes after every commit (its worlds don't exercise these layers' changes).

## Drafts

- `draft-arctic-coastal-sea-summers-too-cold.md` (climate): Laptev / Kara coasts never thaw (PW-230's remaining cause).
- `draft-wave-storm-winds-over-land-locked-seas.md` (needs-decision): the enclosed seas' wind (PW-075 / PW-296).
- `draft-earth-rock-map-carbonate-shelves.md`: Earth's warm shelves should be carbonate (PW-323's reef drop on Earth).
