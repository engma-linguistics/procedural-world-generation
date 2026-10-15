# Physics audit (PW-245): ice, glacial time zoom, vegetation

Area: `planet/icemass.py`, `planet/timezoom.py`, `planet/timezoom_kernels.py`, `planet/finish.py`, the ice,
sea-level, CO2/weathering and ice-albedo parts of `planet/tectonics/earth.py`, `planet/tectonics/isostasy.py`
(ice load, land_view), `planet/vegetation.py`, `planet/zoom_vegetation.py`. Audited on main at 10b89eb.

How each item is graded (the owner's rule): a **sound approximation** is a known simplification with a physical
basis, however crude. A **bandaid** forces the answer, hides a process error, or only works on Earth. Most of
this area is sound approximations. I found no Earth-keyed branch on generated planets, no sign-flipped term and
no loosened test without a stated reason. The real findings are two places where one process gets two different
rules, and one geometric shortcut that shapes the outputs.

## What I measured

Scratch probes are in the session scratchpad (`iceveg/`). They were not committed.

- **L5, seed 2, 1000 Myr** (`run_probe.py`, 251 climate updates):
  - Sea level from ice: −67 m on average, −371 m at the lowest, below −150 m 18% of the time (this is PW-240).
  - The CO2 index sat at its ±1.5 clamp in 1 of the 251 updates.
  - The ice reached ICE_MAX (4000 m) in up to 23 cells.
  - Ice surfaces went up to **9.4 km** and coldest months down to **−111 °C**. At t ≈ 968 Myr, the 33 iced
    cells with a surface above 5 km had a bed of 4.8 km and 2.2 km of ice on average.
  - Up to 216 iced cells had their bed pressed below sea level. None had crust below sea level.
- **L4, seed 1, 300 Myr** (`smb_probe.py`): land cells where bare-ground snow outlasts the summer, averaged over
  the orbits. The run's new-cap rule (cover 0) against the time zoom's rule (sheet cover with the LOCAL floor,
  0.3):

  | Global shift | Run's rule (cells) | Time zoom's rule (cells) |
  |---|---|---|
  | dT 0 | 13 | 14 |
  | −3 | 16 | 19 |
  | −6 | 18 | 24 |
  | −9 | 27 | 39 |

  Taking out the melt hold on bare ground lowers the run's counts by only 2 (13→11, 27→25).
- `tests/test_timezoom.py` and `tests/test_isostasy.py` pass (16 tests). The time zoom's ice budget closes to
  1e-6 (flow conserves ice exactly; volume changes only by mass balance and calving).

## Findings

### 1. Med: the run's ice thickness is a Nye profile stacked on the bed, whatever the bed's height (a cause of PW-226)

**Where:** `earth.py:275-288` (`ice_sheets`).

**What:** the thickness is `sqrt(2 tau/(rho g) x distance from the edge)`, added on top of the bed. On a range
that rises inward from the sheet's margin, the surface therefore climbs by the bed's relief plus the profile. A
real sheet's surface rises from its margin's elevation, and over high bed it is thinner (the ice drains off the
high ground). That is why real ice surfaces stop near 4 km.

**Evidence:**
- L5 seed 2: 2.2 km of ice on 4.8 km beds, surfaces up to 9.4 km, 11-14 cells with coldest months below −90 °C.
- At L4 the grid makes it worse: a cell one hop in from the edge is ~450 km in, so it gets ~2.3 km of ice. This is
  PW-226's 2.4 km cap on a 7 km range.

**Grade:** a geometric shortcut that is not technically sound. It shapes the ice volume on mountainous
continents, the ice-surface climate and the cold bound in `test_values_sane`.

**Fix (simple, sound):** carry each sheet's edge-bed height through the BFS from the edge. Take the surface as
`max(bed + small, bed_edge + Nye(d))` and the thickness as surface − bed, at least the margin's thickness.

**Likely effect:** thinner caps on high ranges, surfaces nearer 4-5 km, a little less ice volume, and PW-226's
−95 °C bound restorable.

**Draft:** `draft-audit-ice-veg-nye-on-high-bed`.

### 2. Med: a new ice cap starts under a stricter rule in the run than in the time zoom (part of the time zoom's drift and of PW-240 / PW-033)

**Where:** `earth.py:260` against `timezoom.py:643` and `icemass.py:52-62`.

**What:**
- The run's seed test for a new cap is `balance(h=0, cover=0)`: no summer damping on lying snow.
- The time zoom damps every lying snowpack by `summer_damp x sheet_cover`, and `sheet_cover` is at least LOCAL
  (0.3) everywhere, even with no ice anywhere.
- So bare ground glaciates more readily in the time zoom. On the L4 climate, 44% more bare-ground cells hold
  their snow at dT −9 (39 against 27).
- The run does use the LOCAL floor in its second test (`acc_ok`, h = 330 m on every cell), so LOCAL works in the
  run only on cells next to ice.

**Why it matters:**
- The overview says a time zoom from a run's moment starts "close to its own balance". In fact it drifts to more
  ice (a further −68..−144 m). This rule difference is one cause of that drift.
- LOCAL itself is a knob that is known to be tuned for Earth's inception: "the 0.3 share is what lets Earth's time
  zoom glaciate", PW-240 option B.

**Grade:** an inconsistency. LOCAL, set to make Earth glaciate, is close to a bandaid.

**Draft:** `draft-audit-ice-veg-new-cap-rule-run-vs-timezoom` (needs-decision; options and lean are in it).

### 3. Low-med: two ice-surface climates for the same ice

**Where:**
- `climate.py:2046-2063` (`ice_surface`): 10 °C × ice_cover colder all year, and the summer capped at
  half of its positive part.
- `icemass.py` and `timezoom_kernels.climate_step`: 2 °C (ALBEDO_SHARE × 10) all year, plus a summer damping by
  sheet_cover and the melt hold.

**What:**
- The run's ice comes from icemass. The run's keyframe temperatures on ice, its Köppen and the zoom's ice surfaces
  come from `ice_surface`.
- So does the softness factor inside `ice_sheets` (`earth.py:286`).
- The time zoom's frames, and the finished worlds made from them, report icemass-style temperatures.
- In winter, on a big sheet, the two rules differ by up to ~8 °C. That is part of PW-226's −105 °C.
- PW-112 already says the 10 °C compensates a too-warm polar base. Since PW-190 it no longer sets the ice extent;
  it only sets what is shown.

**Grade:** the 10 °C is a known bandaid (PW-112). Keeping both rules is the inconsistency.

**Fix (simple):** report the ice surface's temperatures from `climate_step`'s own outputs (t_ann, t_warm,
t_cold at the ice's thickness), and drop `ice_surface`'s 10 °C for land ice.

**Draft:** `draft-audit-ice-veg-two-ice-surface-climates`.

### 4. Low: weathering's temperature sensitivity counts runoff twice

**Where:** `earth.py:25,67`.

**What:**
- `WEATHER_K` = 0.12/°C is described as 0.09 (activation energy) + 0.03 (runoff).
- The sink is `sim.removed x warm`, and `removed` is erosion, which already scales with rain ((P/800)^0.8).
- The runoff part is therefore counted twice.
- The value was doubled from 0.06 in PW-235, whose aim was to shorten cold eras (a KPI). The physics behind it
  (Walker et al., GEOCARB) is sound.

**Fix:** 0.09. It is a small change, and it slightly weakens the thermostat.

**Draft:** `draft-audit-ice-veg-weathering-runoff-twice` (xs).

### 5. Low: a finished world's orbital anomaly uses the bed, not the surface, as land

**Where:** `finish.py:145`.

**What:** `land = st["elevation"] > 0` is the bed. Ice cells whose bed is pressed below sea level get the sea's
insolation response (×0.3, no snow brightness) instead of the land's that the time zoom used (`timezoom.py`,
land = surface > 0). The effect is small: it touches only cells under thick ice, where the response is 0.2×
anyway.

**Fix:** `land = st["elevation"] + st["ice"] > 0`.

**Draft:** `draft-audit-ice-veg-finish-orbit-land` (xs).

## Checked and clean (or a sound approximation)

- **Sea level from ice, run** (`earth.py:154`): −0.9 × V / ocean area. No run ice stands on crust below sea level.
  Inland ice pressed below sea level is rightly counted in full: vaf + pov reduces to ρi/ρw × V. The 0.9 against
  917/1028 = 0.89 is a 1% overcount. Sound.
- **Sea level from ice, time zoom:** above flotation plus the potential ocean volume (Goelzer 2020) is correct, and
  the test closes. The fixed starting ocean area understates a 120 m fall by ~3-4%. Sound.
- **Shallow-ice flow:** conservative (the outflow limiter, H ≥ 0). `d_cap` is a stability limiter for
  unresolved margins. Sound.
- **Vialov-style thickness factors** (`earth.py:285-287`): accumulation^(1/8) and the 0.7 for temperate ice match
  the n = 3 scaling (A ratio ~15 → 15^(-1/8) ≈ 0.71). The clip of 0.75-1.15 is a mild bound. Sound.
- **Melt hold on seasonal snow over bare ground:** it could double-count with degree-day factors calibrated on air
  over snow, but it moves the new-cap snowline by only ~2 cells in 27 at L4. Sound, small.
- **Refreeze as 60% of snowmelt:** never more than Reeh's 60%-of-snowfall cap, so it is conservative. Sound.
- **Insolation** (Berger, Kepler months): correct and tested. `insol_k` 0.25 °C per W/m² is at the high end, but
  it has not changed since the time zoom was created. Sound.
- **Glacial isostasy:** 917/3300 ≈ 0.28, flexure over 150 km, ELRA with a 3 kyr time constant. All are textbook
  values. Sound.
- **Earth-only branches** (`anchor=obs`, `phases=eemian`, `baseline=obs`, `orbit_ref=today`): only used for the
  Earth source. They correct Earth's input, not generated planets. Acceptable as the "delta method".
- **Ice-albedo measured from Earth's present ice** (EARTH_ICE 3.1%): keeps dT = 0 equal to Earth's climate with
  its ice. Sound.
- **CO2 clamp ±1.5:** hit once in 251 updates. Sound (a saturation bound).
- **Vegetation:**
  - GlobFIRM replaced by a logistic that burns ~1/3 per year at 5 dry months. Documented and savanna-realistic.
  - The tree-cover cap from P/PET (Sankaran 2005), CO2 fertilisation (+12% per CO2 unit for C3) and the snow
    masking by conifers are sound.
  - The grazing placeholder is a known bandaid (PW-207).
  - The ±20% band on rain recycling and the ±2 °C albedo cap are explicit loop limiters, documented. I count them
    as sound limiters, not bandaids.
- **Zoom vegetation:** the pull (CORR) of pixel means toward the coarse cell's cover, with its ratio clipped to
  0.5-2, keeps the scales consistent. It is a mild mask, documented, and it does not use Earth targets.
- **Test history:**
  - `test_values_sane`'s cold bound went from −95 to −110 °C (1a2b851, PW-226; finding 1 is its cause).
  - `test_zoom_ice`'s snowline went from >6 to >8 °C (d5e00f1), with a physical reason (a maritime snowline at
    1.8 m of rain).
  - `test_finish`'s floored-bed assert was replaced when beds became true beds (11b2ee3).
  - No skips or xfails were added.

## Appendix: inventory

| file:line | what | justification found | grade / verdict |
|---|---|---|---|
| icemass.py:34 SNOW_H 20 m | snow-bright thickness | none beyond phase-in | sound / fine |
| icemass.py:35 SUMMER_DAMP 0.6 | summer damping on a big sheet | Antarctica/Greenland summers vs bare ground (docstring) | sound / weak |
| icemass.py:36 MELT_HOLD 0.5 | positive temperatures halved on snow and ice | Greenland ablation-zone vs tundra July temperatures | sound / weak (small effect measured) |
| icemass.py:38 BARE_SHARE 0.3 | bare ice keeps 30% | none | sound / weak |
| icemass.py:39-40 ALBEDO_SHARE 0.2, ALBEDO_H 800 | 2 °C all-year cooling on thick ice | inversion, katabatic air | sound / fine |
| icemass.py:41 EDGE_H ~330 m | margin thickness (Nye, 10 km in) | Nye profile, 50 kPa | sound / fine |
| icemass.py:43-46 PDD_SIGMA 5, DDF 3/8, REFREEZE 0.6 | PDD model | Reeh 1991, Braithwaite 1995 | sound / fine |
| icemass.py:47 PRECIP_K 0.07 | Clausius-Clapeyron | physical | sound / fine |
| icemass.py:49 LOCAL 0.3 | floor of sheet_cover | "lets Earth's time zoom glaciate" (overview §2.8) | bandaid-ish / suspicious (finding 2, PW-240 B) |
| icemass.py:61 polar ramp 15-50° | no damping in the tropics | as climate.ice_cover | sound / weak |
| icemass.py:69-70 OBL_AMP 1.2, ECC 0.03, INSOL_K 0.25, INSOL_SEA 0.3, ICE_ABSORB 0.2 | orbit cycle for the run's average | the time zoom's own values | sound / fine |
| timezoom_kernels.py:65 ps clip 0.02-3 | rain scale bound | none | sound / fine (rarely binds) |
| timezoom_kernels.py:89 rain/snow −2..+2 °C | snow share ramp | standard | sound / fine |
| timezoom_kernels.py:157 d_cap | diffusivity cap | unresolved margins | sound limiter / fine |
| timezoom.py:126 TZParams.insol_k 0.25 | °C per W/m² | none (not tuned since creation) | sound / weak (high end) |
| timezoom.py ice_absorb 0.2, absorb_km 600 | snow albedo against orbit | comment: wider melts Earth's Eemian | sound / weak |
| timezoom.py anchor (obs/balance), anchor_max 15 °C | Earth start cooling | PW-039, Earth only | Earth-only correction / fine (not on generated planets) |
| timezoom.py co2_cool 2.5, co2_max 1, average_room 0.5 | CO2 and albedo feedback caps | Earth LGM CO2, PW-031 | sound / weak (room tuned) |
| timezoom.py:620 excess clip −0.5..room | CO2 bound | saturation | sound / fine |
| timezoom.py ice_albedo 0.75, max 2 | global albedo | "local part is in the ice surface" | sound / fine |
| timezoom.py flow_a 1e-16, enhancement 3 | Glen's law | standard ice-age values | sound / fine |
| timezoom.py:637 margin edge_h | sub-grid margin | the cliff-like margin at ~110 km cells | sound / fine |
| timezoom.py calving 1/yr, calve_depth 1500 m | calving law, deep-basin ice | PW-199 | sound / weak |
| timezoom.py:432 ocean_area fixed | sea-level area | none | sound / fine (~3% error) |
| timezoom.py RHO_I/RHO_W 917/1028 | flotation | physical | sound / fine |
| earth.py:25 WEATHER_K 0.12 | weathering sensitivity | GEOCARB 0.09 + 0.03 runoff | double count / weak (finding 4) |
| earth.py:70 npp factor 1+0.5·clip(npp/800, 0, 1.5) | biological weathering | GEOCARB | sound / fine |
| earth.py:24 EARTH_ICE 0.031 | ice-albedo reference | climate calibrated with Earth's ice | sound / fine |
| earth.py:115 albedo tanh, ice_albedo_max 3 | albedo saturation | comment | sound / fine |
| earth.py:120 clip(co2, ±1.5) | CO2 bound | none; hit 1/251 | sound / fine |
| earth.py:154 −0.9 V / A | sea level from ice | ice density | sound / fine |
| earth.py:212 ICE_TAU 50 kPa | Nye yield stress | standard range 50-100 | sound / fine |
| earth.py:215 ICE_MAX 4000 | thickness cap | none (Antarctica 4.8 km); binds at L5 | clamp / weak |
| earth.py:216 ICE_CALVE 5e4 m²/yr | calving cost | ~0.7 m/yr per coastal cell | sound / fine |
| earth.py:218 ICE_RINGS 40 | ablation-zone limit | none; not binding | sound / fine |
| earth.py:260 smb0 with cover 0 | new-cap test | none | inconsistent / suspicious (finding 2) |
| earth.py:275-276 Nye from edge on bed | thickness | Nye | not sound on high bed / suspicious (finding 1) |
| earth.py:285 snow clip 0.75-1.15, ^0.125 | Vialov accumulation | n = 3 scaling | sound / fine |
| earth.py:286 own uses climate.ice_cooling (10 °C) | softness temperature | none | inconsistent / weak (finding 3) |
| earth.py:287 soft 0.7-1 | temperate ice softer | A ratio^(−1/8) | sound / fine |
| climate.py:1291 ice_cooling 10 °C | ice-surface cooling | PW-112: compensates a warm polar base | bandaid (known, PW-112) / finding 3 |
| climate.py:2059 summer ≤ half of positive part | melt cap | as MELT_HOLD | sound / weak |
| isostasy.py:54 ICE_SINK ρi/ρm | load | physical | sound / fine |
| isostasy.py:55 FLEX_KM 150 | flexure | lithosphere | sound / fine |
| isostasy.py:56 BED_FLOOR 1 m | land_view | bookkeeping for land tests | sound / fine |
| finish.py:145 land = bed > 0 | orbit mask | none | bug / low (finding 5) |
| vegetation.py:131 _TUNE overrides | PFT knobs | "tuned on Earth with veg_check" | tuned parameters, per PFT (not regional) / weak |
| vegetation.py:163 EPS_SCALE 0.8 | NPP scale | Earth land NPP | tuning of one global knob / weak |
| vegetation.py:440, 625 CO2 clip | C4 envelope, C3 fertilisation | physical sign | sound / fine |
| vegetation.py:701 GRAZE 0.05 | grazing placeholder | decision 8, PW-207 | bandaid (known) |
| vegetation.py:727 FIRE_MAX/MID/WIDTH | fire curve | GlobFIRM's savanna shortfall | sound / weak |
| vegetation.py:728 FUEL_MIN/SPAN | fuel threshold | PW-234 | sound / weak (known) |
| vegetation.py:793 cost clip 0.3-1 | stand cost | stunted treeline trees | sound / fine |
| vegetation.py:799 tree cap from P/PET | water cap on canopy | Sankaran 2005 | sound / fine |
| vegetation.py:806-807 kdec clip, ignition | litter decay, lightning | Q10 | sound / fine |
| vegetation.py:954 lat < 45 | montane-conifer naming | classification only | naming rule / fine |
| vegetation.py:1124-1128 albedos | PFT albedo | literature values | sound / fine |
| climate.py:1339-1341 et_band 0.2, albedo_cap 2 °C | feedback limiters | "can't rain itself into existence" | sound limiter / weak |
| zoom_vegetation.py:66-67 SLOPE_DT, MAX | slope temperature | radiation index | sound / fine |
| zoom_vegetation.py:368 CORR, ratio clip 0.5-2 | pixel-to-cell pull | consistency between scales | mild mask / weak |
| zoom_vegetation.py:79 FW_MAX 0.75 | flooded share | as vegetation.flooded | sound / fine |
