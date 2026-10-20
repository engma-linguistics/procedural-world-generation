# PW-448 diagnosis: why Earth's time-zoom glacials are only ~1.9 C colder (2026-10-20, agent pw448)

**Short answer.** At the ice it actually grows, the time zoom's feedback is about as strong as Earth's:
0.044 C per metre of sea level at the deepest glacial, against Earth's ~0.048 (about -6 C at -125 m).
The glacial is shallow because the ice stays small, and the main reason it stays small is the
ice-albedo rule's levelling-off. That rule is the run's (`earth.py`), which the time zoom copied in PW-030.
Its cap is set as if Earth's LGM ice-sheet cooling (~2.5-3 C) were the whole ice albedo, today's ice
included, when it is the change from today. So it gives only 1.3 C for going from today's ice
(2.8% of the planet) to the LGM's (~8%). Earth's value is ~2.6 C. The loop is close to a gain of 1, so
this matters a lot: with the levelling-off removed (diagnostic `ice_albedo_max=30`), the Earth zoom
reaches **-71 m and -4.1 C**, has 5 endings and no backstop, and keeps the same interglacials.
There is still no Laurentide south of ~55 N, even at an Earth-like -5 C. That half of the ticket is not
a forcing problem. It is the Canadian interior's balance and the margin advance (PW-033, PW-435).

All numbers: Earth L6, default knobs, 600 kyr, in memory (the same run as showcase 755514, min -42.8 m at
314.5 kyr). Scripts are in the session scratchpad `pw448/`: `diag.py` (instrumented zoom), `gmean.py`
(decomposition), `probe.py` (fixed-orbit cooling scan) and `sites.py`.

## 1. The glacial maximum's cooling, term by term (vs the start = today's interglacial)

How the code builds it: `Forcing.update` gives dTg = CO2 + ice albedo, and nothing else is global.
`climate.compute` applies dTg as a prescribed offset (0.5x tropics .. 1.5x poles), with no further
feedback. The orbit is local only (`insol_k` 0.25 C per W/m2 on land). The ice sheets' own climate
(elevation, ice surface, `ice_air`) is local too.

| term | model at its deepest (-42.6 m, 6.0% of the surface iced) | model if its ice were LGM-sized (-120 m, ~8%) | Earth LGM (-125 m) |
|---|---|---|---|
| CO2 (slaved to ice volume, 3 kyr lag) | **-0.65 C** (target -0.89; ~-0.8 W/m2 at 0.8) | -2.5 C (`co2_cool`) | CO2 190 vs 280 ppm: -2.1 W/m2 (5.35 ln(190/280)) -> -1.7 C. CH4+N2O another -0.6..-0.7 W/m2 -> -0.5 C |
| ice albedo (global, from the area) | **-1.21 C** (3.1% of the planet newly iced; ~-1.5 W/m2) | -1.3 C (tanh levelling-off) | land ice -3.2 W/m2 (Köhler et al. 2010), -3 to -3.5 (Hansen et al. 2008, ice sheets + sea level) -> -2.6 C |
| the sheets' own climate (elevation, ice surface; area mean of `climate.compute`, no dT) | **-0.31 C** | ~-0.8 C (scaled) | (inside the -3.2 above: topography) |
| orbit, global annual mean | **+0.03 C** (+0.31 W/m2: e 0.046 vs 0.017) | ~0 | ~0 (LGM orbit close to today's) |
| orbit, NH land 50-70 N, May-Aug | -2.3 C (65 N months: +22 +24 +2 -26 -34 -21 W/m2 from the March equinox on) | | 116 ka: 65 N June ~-40..-50 W/m2 |
| vegetation (forest to tundra; snow masking) | **0** (`climate.compute(veg=None)` in the time zoom) | 0 | -1.1 W/m2 (Köhler 2010) -> -0.9 C |
| dust | **0** (PW-030 tried snow darkening, not the radiative term) | 0 | -1 W/m2 (range -0.3..-1.9; Köhler 2010 has -1.9) -> -0.8 C |
| **total, area mean of the actual climate** | **-1.95 C** (dTg -1.86) | ~-4.6 C | **-6.1 C** (Tierney et al. 2020, -5.7..-6.5); -4.5 +- 0.9 (Annan et al. 2022) |

Sensitivity used for Earth's column: ~0.8 C per W/m2 including the water-vapour, lapse-rate, cloud and
sea-ice feedbacks (Hansen et al. 2008: 3 C per 4 W/m2 = 0.75; PALAEOSENS 2012: S[CO2,LI] ~0.6-1.3).
Total Earth forcing is ~-8 W/m2 (-7..-10). The model's terms are temperatures with that amplification
already inside them: `co2_cool` 2.5 C per -90 ppm is 1.2 C per W/m2 for CO2 alone, or 0.9 for all GHGs.
The albedo rule's linear slope of 1.5 C per 3% of the planet is 0.5 C per 1%, Earth's 2.6 C over 4.9%
being 0.53.

## 2. The questions, answered with numbers

**Does the forcing-to-temperature chain lack the fast-feedback amplification?** No. Both global terms
are temperatures calibrated with it: CO2 equals or exceeds Earth's per unit of ice, and the albedo
slope equals Earth's at small extents. Per metre of sea level at the deepest moment the model gives
0.044 C/m against Earth's ~0.048 (0.045 with the local sheet climate).

**Is CO2 slaved to the extra ice (chicken and egg)?** Yes, structurally. `co2_target` is -2.5 C x
(-sl/120). At -43 m that is a target of -0.89 C, and only -0.65 C is realised because the glacial
maximum is a ~10 kyr spike and the lag is 3 kyr. Earth's CO2 runs ahead of its ice. At MIS 5b-5d (sea
level -40..-50 m) it was ~230-240 ppm, ~45-55% of the full drop, against the model's 26-36%. At MIS 4
(-80 m) it was ~200 ppm (~85%). A concave CO2(ice) or a temperature-driven CO2 would add ~0.3-0.5 C at
-43 m. That is measurable but secondary: raising `co2_cool` to 4.0 deepened the glacial only
-42.8 -> -45.3 m.

**Does Earth wrongly get a run moment's halved CO2 cap?** No. `sim.py`: `start=auto` is
`interglacial` for Earth, so `room = 1.0` and the clip is at 120 m, which is never reached.

**The Canadian interior at glacial orbits.** Bare-land balance and warmest month on today's surface
(`probe.py`). The orbit is the series' coldest NH summer (t=592 kyr: obliquity 22.3, e 0.038,
perihelion 356 deg; 65 N months 3-4 = -32 W/m2). The full climate is refreshed at each prescribed dTg.

| region (ice-free land) | obs Tjul | model Tjul, today | glacial orbit, dTg 0 | dTg -2 | dTg -4 | dTg -6 |
|---|---|---|---|---|---|---|
| Canada 50-70 N, 110-60 W | 12.5 | 15.6 | 17.7 C, SMB -14.7 m/yr | 15.1, -11.5 | 12.7, -9.1 | 10.5, -7.0 (9% of area positive) |
| Keewatin box | 11.8 | 13.6 | 15.3, -10.3 | 12.4, -7.5 | 9.8, -5.5 | 7.3, -3.9 (1%) |
| Labrador box | 11.9 | 17.4 | 20.1, -17.2 | 17.5, -13.3 | 15.2, -10.4 | 12.8, -7.8 (1%) |
| Fennoscandia | 14.2 | 9.3 | 10.7, -6.1 | 8.0, -4.2 | 5.1, -2.7 | 2.6, -1.5 (25%) |

(SMB is the potential balance of bare ground in m of ice per year. It goes positive where the
warmest month is <= ~0-1 C, consistent with Ohmura et al. 1992's equilibrium-line summer
temperatures for 300-1000 mm of snow.)
- The Canadian interior is far from positive balance. Extrapolated, Keewatin needs dTg ~-9 C and
  Labrador ~-11 C at that orbit. In the zoom itself, at the deepest step, Keewatin has Tjul 11.3 C and
  SMB -7.4, Labrador 15.2 / -12.8, the Hudson Bay lowlands 15.4 / -13.5. Only Baffin, Ellesmere,
  Alaska, Novaya Zemlya and Norway are iced.
- The model's Labrador summer is 5.5 C too warm, Canada's interior 3.1 C and Baffin 3.0 C, while
  Fennoscandia is 4.9 C too cold (the PW-033 regional bias, still there). The observed baseline
  (`baseline=obs`) does not help the depth: -29 m, with Laurentide 2.4 Mkm2 and no Fennoscandian ice.
- At this orbit the warmest month is *warmer* than today's (+1.5..3.5 C). The insolation deficit falls
  in Jul-Sep, and May-Jun gain (+10..+28 W/m2). The May-Aug land mean is -2.3 C. A summer-sun minimum
  does little to the melt season's peak. That is a real feature of the orbit (perihelion near the
  March equinox), not a bug found here.
- Even with the full Earth-like cooling (variant "both", -5.1 C area mean), the Laurentide stays
  2.0 Mkm2 with its southmost ice at 54.9 N. The new NH ice (19.9 Mkm2, mean latitude 64.9 N) goes to
  Siberia, Alaska and the Arctic islands. The geography of the LGM is not a global-forcing problem.

## 3. Measured sensitivity of the depth to each term (Earth, 600 kyr)

| variant | min sea level | dTg at min (CO2 / albedo) | area-mean T change | iced share at min | Laurentide Mkm2 / southmost | Fennoscandia Mkm2 / southmost | interglacial ice vol (Mkm3) | endings (kyr), backstops |
|---|---|---|---|---|---|---|---|---|
| default (= 755514) | -42.8 m | -1.86 (-0.65 / -1.21) | -1.95 | 6.0% | 1.6 / 54.9 N | 1.5 / 54.4 N | 28.1 | 17, 43; 1 |
| `baseline=obs` | -29.1 | -1.56 (-0.54 / -1.02) | -1.58 | 4.5% | 2.4 / 53.9 | 0 | 30.3 | 16, 16.5; 2 |
| `co2_cool=4.0` | -45.3 | -2.39 (-1.16 / -1.23) | | | | | 28.1 | 45.5, 42.5; 0 |
| `ice_albedo_max=30` (~linear) | **-70.8** | -4.10 (-1.35 / -2.75) | -4.07 | 6.7% | 1.9 / 55.9 | 2.0 / 54.1 | 29.0 | 41.5, 49.5, 41.5, 18, 74; 0 |
| both | -74.8 | -5.25 (-2.28 / -2.98) | -5.13 | 7.0% | 2.0 / 54.9 | 2.2 / 54.1 | 29.2 | 19.5-72.5 (6); 0 |
| obs + both | -43.2 | -3.35 | | | | | 31.8 | 42.5, 43; 0 |

(Laurentide = ice at 100-60 W, 40-75 N, Baffin included. Fennoscandia = 0-40 E, 50-72 N. The
interglacial volume is the mean over the highest 5% of sea levels after 50 kyr. The start is 28.0 Mkm3.)

## 4. What is wrong, ranked

1. **The ice-albedo levelling-off is mis-anchored (run rule, shared).** `ice_albedo_max` 3.0 is
   annotated "Earth's LGM ice sheets: ~2.5-3". That literature figure is the LGM *change* from today,
   but the tanh counts today's 2.8% in it (1.4 C of the 3), leaving 1.3 C for 2.8 -> 8%, about half of
   Earth's ~2.6 C. Physically, new ice spreading equatorward gets *more* sun per km2, not less. It is
   the single biggest measured lever: -43 -> -71 m, with endings restored (5, no backstop) and
   unchanged interglacials. It is shared with the run (`planet/tectonics/earth.py`, not editable here,
   PW-438 in flight). Changing it only in the time zoom would undo PW-030's consistency. It is a
   judgement call, so it goes to a needs-decision draft, not a fix.
2. **The Canadian interior's balance and the sheet's advance (PW-033, PW-435).** The interior lacks
   9-11 C of summer cooling at glacial orbits, the model's Labrador is 5.5 C too warm, and a front
   advances by about one ring per step under an edge's balance. Even at Earth-like global cooling the
   ice goes to Siberia and Alaska, not south of 55 N in America or into Germany. This sets the LGM's
   geography and most of its remaining depth (-75 vs -125 m).
3. **Missing global terms: vegetation (-1.1 W/m2) and dust (~-1 W/m2), ~-1.7 C at the LGM.** The time
   zoom calls `climate.compute` with `veg=None`, so a glacial's forest-to-tundra snow-albedo change, the
   classic inception amplifier, is absent. This is a sizeable integration (vegetation.model needs the
   flow, lakes and clouds) and belongs in the same decision.
4. **CO2 slaved linearly to the ice volume.** It is ~10-20 percentage points of the full drop behind
   Earth's early in a glacial. Secondary: ~0.3-0.5 C at -43 m, and `co2_cool` 4.0 gave only -2.5 m.
5. Not wrong: the fast-feedback amplification (present in both terms' calibration), Earth's CO2 cap
   (room 1), and the CO2 sensitivity per ppm (slightly generous).

The loop gain is the reason a 0.4 C change in the albedo slope at the base state moves the glacial by
~30 m. The Earth zoom sits near a gain of 1 (unforced prescribed -3 C gives -60 m and -5 C gives -137 m
in 150 kyr, PW-435), so any honest correction to the feedback slope changes the depth strongly. That
is also why it should be fixed in the shared rule and not tuned in the time zoom.

## Sources (values as quoted in them)
- Tierney et al. 2020, Nature 584: LGM global mean -6.1 C (95% -6.5..-5.7). Annan et al. 2022, Clim.
  Past 18: -4.5 +- 0.9 C. Osman et al. 2021: -7.0 C.
- Köhler et al. 2010, QSR 29: LGM forcings: CO2 ~-2.0, CH4+N2O ~-0.7, land-ice albedo -3.2, vegetation
  -1.1, dust -1.9 W/m2 (uncertain).
- Hansen et al. 2008, Open Atmos. Sci. J. 2: GHG ~-3, ice sheets + sea level -3.5 +- 1 W/m2, 0.75 C per
  W/m2. PALAEOSENS Project Members 2012, Nature 491.
- Bereiter et al. 2015 (EPICA CO2: LGM ~190 ppm, MIS 4 ~200 ppm, MIS 5b-d 230-240). Myhre et al. 1998
  (5.35 ln C/C0).
- Ohmura et al. 1992, J. Glaciol. 38: summer temperature at the equilibrium line vs accumulation.
- Svendsen et al. 2004 (Eurasian LGM margins), as the owner's comparison map.
