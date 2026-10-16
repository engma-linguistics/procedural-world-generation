# Polar-climate bundle: PW-335, PW-336 (A), PW-332, PW-337

Branch `worktree-agent-a8a1bc9cbeeeba09d`, from main a876572 (merged with main 04799b9 afterwards). One model commit (baabbba). Measured on Earth L6 (dT 0 unless given) with `tools/ice_probe.py`, `tools/earth_check.py`, `tools/coast_check.py`, `tools/scorecard.py` and `tools/health.py --quick`, before (a876572) and after.

## Short answer
- **Done:** PW-335 (frozen-sea summer air, as designed), PW-336 option A (the sheets' own summer air carried along the winds; `icemass.sheet_cover` is the surface's own `LOCAL` share), PW-337 (the sea-ice inversion levels off), and two sound fixes for PW-332's snowfall.
- **The snowfall cause (PW-332).** Two errors in what the rain kernel sees near ice and the poles:
  1. *The vapour rode the polar cell's shallow outflow.* The rain kernel moved vapour with the surface wind, whose polar cell drifts equatorward poleward of 60° (up to 0.3 at 75°). That is cold air draining off the pole under the polar inversion (katabatic outflow on Antarctica). It holds little of the column's vapour, which sits above the inversion in warmer air and reaches the polar coasts with the storms. The kernel's mean wind blew the vapour off Antarctica everywhere south of 60S, against the eddy mixing that brings it in. Fix: the rain's wind leaves that drift out (`climate.polar_drift`). The air temperatures keep it, because the drift does carry the surface air's cold.
  2. *The kernel saw the bed, not the ice.* `_season_inputs` took heights from the bed, while its air temperatures sit on the ice surface. Over a sheet the sea-level air mass came out LAPSE x the ice thickness too cold (~16 °C for 2.5 km), and the ice's slopes gave no orographic lift. Fix: heights from the surface.
- Antarctic land snowfall 70-80S: **77 -> 158 mm** (GPCP 210); ice shelves 85 -> 156 mm (Ross/Ronne observed ~100-250); Greenland's ice 207 -> 304 mm (GPCP 375). Antarctica's grounded ice in the probe averages 170 mm/yr against ~170 observed.
- **Probe at dT 0: 0.10% -> 2.33% after 8 updates**, nearly held (still losing ~12 margin cells per update). **dT -6: -44 -> -66 m, still growing** (-71 m at 13 updates); dT -9 -90 m, dT -12 -142 m, both levelling off.
- **Not met in full:** the margins still get about half of GPCP (bed 0-500 m: 167 vs 364 mm). That is the high-latitude seas' moisture supply (Southern Ocean 55-65S at 0.4 of GPCP, the North Atlantic/Pacific too). With Antarctic snowfall x1.5 as a diagnostic the probe holds (965 cells, no loss after the 2nd update). That gap is PW-015's storm-track moisture transport, not a polar problem (draft `draft-polar-storm-track-moisture-half.md`). The sea column 70-80S that PW-332's checkbox quotes (412 mm) is earth_check's **sea** column (the Ross, Weddell and Amundsen seas): 200 -> 235. Antarctica's land column is the 210 mm one.
- **Generated planets:** ice now answers cooling about as Earth's does. Seed 2 has a new deep spell, -340 m at the end of its run (global 3.0 °C). Seed 11's cold era is -246 m (was -264). Both of those eras reach global 3.0-3.2 °C, below the health envelope's 8 °C (the LGM was ~8 °C): PW-240's climate-drift question, not a runaway. On Earth's fixed geography the ice levels off at every dT.

## 1. What changed (planet/climate.py, icemass.py, timezoom.py)
| | before | after |
|---|---|---|
| sea's summer air (`_air_temps`) | sea cells `sst + sea_half + 3 x frozen`; the land's carry `sst + sea_half` | both `max(sst + frozen + sea_half, FREEZE)` (PW-335) |
| air over sea ice, annual / winter | `sst + 3f`, `sst - sea_half + 4.5f` (f = frozen <= 0) | `sst + f + inv`, `sst - sea_half + f + 1.75 inv`, inv = 2f / (1 + (2f/15)^4)^(1/4): the surface inversion levels off near 15 °C annual / ~26 °C winter (PW-337) |
| a sheet's own air mass | local damping of each ice cell's surface, `sheet_cover` = 0.3 + 0.7 x share | the air over the ice: summer warmth x (1 - 0.6 x `air_mass`), `air_mass` = share of the surface within 1000 km under ice (x polar ramp), carried along the summer winds. Surface damping `sheet_cover` = `LOCAL` (0.3) only. The time zoom passes its ice as `compute(ice_air=)` (PW-336 A) |
| rain kernel's heights | the bed | the ice surface (PW-332) |
| rain kernel's wind | the surface wind | the surface wind less `polar_drift` (PW-332) |

Not a knob among them except `INVERSION_MAX` (the deepest annual-mean surface inversions, East Antarctic plateau ~15-20 °C). I didn't tune it to a score: Earth's Arctic moves ~1 °C (annual) / 1.4 °C (winter) from it.

## 2. Temperatures
Ice-free coastal land, warmest month, model / NCEP (°C; with the vegetation feedback, as `coast_check` builds it):

| band | before | after | NCEP |
|---|---|---|---|
| 60-65N | 7.6 | 7.5 | 10.3 |
| 65-70N | 6.4 | 6.3 | 7.9 |
| 70-72.5N | 5.9 | 4.7 | 5.3 |
| 72.5-75N | 4.4 | 2.6 | 3.4 |
| 75-80N | 3.7 | 0.9 | 1.1 |
| 80-85N | 2.8 | -0.8 | -0.8 |
| Arctic Ocean air 75-90N | -9.2 | -0.2 | 1.0 |
| Arctic coastal sea 66-78N, median (PW-333) | -1.3, 47% never thaw | 2.2, 0% never thaw | 2.7 |
| Laptev cell 24686 / Kara cell 20350 | -2.1 / -3.2 | 1.9 / 1.6 | 4.9 / 2.5 |

So 70-85N coasts are within 0.8 °C of NCEP (PW-335's acceptance). Waves (coast_check): Laptev 0.0 -> 3.7 kW/m, Kara 0.0 -> 4.8 (observed 0.3-3), Beaufort 7.3 -> 4.8 (0.5-4); coasts within 2x 25 -> 27 of 33; tides unchanged (24/26). Delta types: Mackenzie and Ganges now match observation (river, tide), and the Lena turns wave-dominated (observed river-dominated; its waves came on).

Stations, warmest month at the station's height (model / climatology):

| station | before | after | obs |
|---|---|---|---|
| South Pole | -10.0 | -18.7 | -28 |
| Vostok | -14.5 | -22.5 | -32 |
| Dome C | -18.2 | -20.1 | -30 |
| Byrd (WAIS) | -7.8 | -8.8 | -14 |
| Halley (shelf) | +5.1 | -1.6 | -4 |
| McMurdo | -2.7 | -2.9 | -3 |
| Mawson | +1.7 | +1.2 | 0 |
| Summit, Greenland | -13.3 | -13.8 | -12 |
| NEEM | -12.1 | -10.0 | -11 |
| Swiss Camp | -4.3 | -4.5 | 0 |
| Danmarkshavn (bare) | +2.0 | +1.1 | +4.2 |

Antarctica's ice by 5° band is now within ~2 °C of NCEP's warmest month (it was 5-11 °C warm south of 75S). The plateau stations are still ~9-10 °C warm: that is the plateau's own inversion (PW-039), which no damping of the bare ground's summer captures. **Greenland's summit isn't overcooled** (-13.8 vs -12): with `air_mass` as the share alone, without the old formula's `LOCAL`, nothing is counted twice. That is why it comes out ~3 °C warmer than the PW-313 write-up's option A.

Side effect: around Antarctica the sea's summer air is now 2-5 °C too warm at 65-80S (70-75S: +3.7 -> +4.1 vs -0.4; 75-80S: -6.6 -> +0.5 vs -1.3). The whole Southern Ocean's air was already 4-8 °C warm (winter too, over the seasonal pack ice), and that warmth reaches Antarctica's margins through the coastal mixing. Draft `draft-southern-ocean-sea-air-too-warm.md`.

## 3. Rain (the PW-332 attribution)
Diagnostics on Earth L6, mm/yr, model / GPCP:

| | base | eddy x3 | leads 0.3 | ice surface only | 3 / 8 extra eddy passes (+ surface) | no polar drift (+ surface) | **bundle** |
|---|---|---|---|---|---|---|---|
| Antarctic land 70-80S (GPCP 215) | 77 | 80 | 84 | 87 | 123 / 184 | 175 | **156** |
| Antarctic land 60-70S (397) | 199 | 209 | 207 | 214 | 276 / 361 | 298 | **259** |
| bed 0-500 m (364) | 92 | 94 | 103 | 85 | 99 / 116 | 168 | **167** |
| shelves (268) | 85 | 88 | 92 | 92 | 120 / 164 | 168 | **156** |
| plateau 2-3 km (121; obs accumulation ~50-100) | 64 | 68 | 68 | 86 | 125 / 190 | 153 | **157** |
| Greenland ice (375) | 207 | 210 | 224 | 316 | 414 / 530 | 377 | **304** |
| Southern Ocean 55-60S, sea (1154) | 434 | 433 | 434 | 433 | 427 / 425 | 428 | **433** |

(The bundle's colder carried sheet air takes back ~15% of the rain gains: colder air over the ice condenses its vapour sooner, upwind.)

- `eddy` x3 does nothing: the storm mixing `diff = clip(0.12 + eddy x B, 0, 1)` is already 1 in every storm track. Extra mixing passes do bring vapour in, but onto the plateau (too wet) rather than the margins, and they don't wet the seas at all.
- The Southern Ocean's own dryness is upstream and global. Over open sea the kernel refills the air to `rh x qs(sst)` every step, so a cold storm-track sea rains about what it evaporates. Tropical land is ~20-90% too wet under the fixed 1000 mm global mean. That is PW-013/015 (draft).
- Orographic lift and condensation in cold air: the lift was missing (fix 2). In cold air the kernel condenses as fast as its vapour allows: q/qs ~0.65-0.8 over the margins. The supply is what limits it.

earth_check, land precipitation by band (model / GPCC, mm): 80-90N 139 -> 184 (168), 70-80N 247 -> 240 (227), **60-70N 487 -> 361 (424)**, 50-60N 757 -> 733 (584). Sea: 80-90N 119 -> 132 (197), 60-70N 349 -> 327 (905), 70-80S 200 -> 235 (412). Regions (model / GPCC): W Siberia 558 -> 427 (503), E Siberia 471 -> 305 (292), N Canada 634 -> 572 (414), Alaska 570 -> 467 (467), European Russia 702 -> 674 (590), Greenland 229 -> 322 (359). The northern vapour now gets past the polar front's convergence (60-65N), which the polar drift piled it into. 60-70N goes from 15% too wet to 15% too dry, and 80-90N from 17% too dry to 10% too wet. Rivers: Lena 20.6k -> 14.7k m³/s (obs 17k), Mackenzie 24.4k -> 20.9k (10k), Yenisei 40.6k -> 10.3k (19.6k; the Ob now drains on its own, 17.9k vs 12.5k).

## 4. earth_check and scorecard
| | before | after |
|---|---|---|
| Köppen main-group agreement (excl. Antarctica) | 71% | 71% |
| exact | 33% | 33% |
| group shares A/B/C/D/E | 20.5/20.3/23.3/26.4/9.4 | 20.5/20.3/23.3/26.3/9.6 |
| band match 70-80N / 60-70N / 50-60N | 82 / 79 / 89 | 83 / 78 / 87 |
| point check exact / group / miss | 29/34/15 | 28/34/16 (Vancouver Cfb -> Dfb: coldest month -2.6 -> -3.1 °C) |
| land mean P (excl. Antarctica) | 1009 | 995 |
| global T | 14.5 | 14.4 |
| land T 80-90N / 70-80N (NCEP) | -19.2 / -17.8 (-21.0 / -16.4) | -20.7 / -18.3 |
| Antarctica T / Tw (NCEP -35.6 / -14.9) | -26.5 / -7.4 | -29.8 / -12.7 |
| Greenland T / Tw (NCEP -21.4 / -5.0) | -27.6 / -9.4 | -27.8 / -9.0 |
| scorecard: Earth group / exact / log-rain corr | 71.3 / 33.0 / 0.61 | 71.0 / 32.7 / 0.60 |
| scorecard seed 1 / 2 at 1 Gyr: land, dry, ice | 34.2%, 17.6%, 0.8% / 33.6%, 16.1%, 2.2% | 33.5%, 24.6%, 1.5% / 30.8%, 17.7%, 1.0% (chaotic re-rolls) |

Rain elsewhere moves by ≤ 4 mm per band equatorward of 50°.

## 5. The probe (`tools/ice_probe.py 0 -6 --regions`, 8 updates)
| | before | after |
|---|---|---|
| dT 0, per update (m) | -33, -20, -12, -6, -2, -0.5, -0.5, -0.5 | -52, -50, -48, -47, -45, -44, -43, -42 (then -41, -41, -40, -40, -39 to 13) |
| dT 0 ice share after 8 | 0.10% (Antarctica 15 cells, Greenland 21) | **2.33%** (Antarctica ~890 of 977 cells, Greenland ~95; 822 / 40 after 16) |
| dT -6 | -47 .. -44 m, 3.1% steady | -54 -> -66 m (8), -71 m (13), 4.1-4.4%, growing |
| dT -9 / -12 (12 updates) | -75 (PW-308) / - | -90 m (6.1%) / -142 m (9.1%), levelling off |

The cells it still loses at dT 0 are margins at 71-75S, at the edge thickness (~310 m), on beds of 50-175 m. Their surface warmest month is 0 to +1.6 °C (Antarctica's coasts: -1 to -4) and they get 150-240 mm of snow, so their balance is -0.8 to -1.3 m/yr. Two causes: the snow (half of GPCP) and the warm Southern Ocean summer air mixed in at the coast. Antarctic snowfall x1.5 (diagnostic) holds the sheet. Greenland decays as in the base (its margins at 70-75N reach a ~0 °C surface summer with 180-280 mm of snow).

## 6. Generated planets (health --quick: 8 L6 seeds x 500 Myr, `--workers 8 --threads 1`)
docs/review/health-polar-before/ (a876572) and docs/review/health-polar-after/. Ice sea level after 50 Myr:

| seed | deepest ice SL m (Myr), before -> after | % of frames < -50 m | spells < -50 m after | min global T C | median SL m | median land % |
|---|---|---|---|---|---|---|
| 1 | -57 (500) -> -30 | 1 -> 0 | - | 9.8 -> 9.0 | 45 -> 81 | 32.5 -> 33.3 |
| 2 | -53 (500) -> **-340 (496)** | 1 -> 6 | 476-500 | 4.2 -> 3.0 | 124 -> -21 | 34.3 -> 33.5 |
| 11 | -264 (188) -> -246 (192) | 16 -> 23 | 148-248 | 3.5 -> 3.2 | -53 -> -21 | 33.9 -> 32.8 |
| 21 | -14 -> -3 | 0 | - | 12.5 -> 12.5 | 26 -> 108 | 35.9 -> 33.1 |
| 3199 | -16 -> -78 (500) | 0 -> 3 | 492-500 | 10.6 -> 8.7 | -48 -> -8 | 33.2 -> 33.4 |
| 42 | -28 -> -6 | 0 | - | 7.7 -> 11.1 | -3 -> 45 | 32.7 -> 34.8 |
| 77 | -41 -> -146 (456) | 0 -> 14 | 440-500 | 6.3 -> 6.8 | 26 -> -42 | 33.0 -> 32.8 |
| 505 | -12 -> -17 | 0 | - | 11.4 -> 11.7 | 32 -> -14 | 33.9 -> 33.5 |

Each run re-rolls its chaotic history, so compare the distribution, not seed by seed. Before, ice answered cooling only below ~4 °C global (seed 2 at 4.2 °C: -53 m). Now a 6-7 °C era (seed 77) holds -146 m, LGM-like. Seed 11's 3.2 °C era: -246 m (PW-240's worst-case goal is -250). Seed 2's 3.0 °C plunge at the run's end: -340 m and 13.5% of the surface iced. That is beyond PW-240's -250 m. It comes with a global 3 °C (dT -11.5), below health's 8 °C envelope (the Phanerozoic's coldest ~10-12 °C, the LGM ~8 °C). So I left the ice rule alone and handed it to PW-240's climate drift rather than damping the ice. Land stays inside its envelope. The top outliers are the before sweep's kinds (giant lakes, little inland drainage); seed 2's ice spell is the one new envelope exit.

Other checks: PW-337 sweep (L4 seeds 1-5, 300 Myr, the coldest month seen at sea in any climate update): -56.8, -55.5, **-114.4**, -81.9, -53.1 °C -> -43.6, -43.2, -57.6, -47.2, -42.4 °C. Land's coldest months are unchanged in kind (-61..-83 -> -65..-81).

## Goldens and tests
Regenerated `tests/golden/climate_L4.json`, `tests/golden/sim_L4_s1_60myr.json`. New `tests/test_polar_climate.py` (5 tests; all fail on a876572). `test_values_sane` and `test_world_soils` now use the frames' own land (`sim.land()`, PW-309's trench; the stored elevation's rounding at 0 m): the re-rolled L4 run hit both edge cases.

## Inbox drafts
- `draft-polar-storm-track-moisture-half.md`: high-latitude seas and Antarctica's margins at ~half of GPCP; the storm-track moisture supply (PW-015). The probe's last gap.
- `draft-southern-ocean-sea-air-too-warm.md`: Southern Ocean air 4-8 °C warm (the sea's own winter air ignores seasonal pack ice; its summer ignores the continent's outflow).
