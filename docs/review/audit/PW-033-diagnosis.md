# PW-033 diagnosis: why the Earth time zoom grows no Laurentide south of ~55 N and no Fennoscandian sheet (2026-10-20, agent pw033)

**Short answer.** The Earth zoom's glacials are pulses, one per precession minimum. All the NH ice grows
from almost nothing to its maximum in ~12 kyr and is mostly gone ~12 kyr later. At the deepest glacial:
300 -> 314 -> 326 kyr gives +3 -> -45 -> -12 m, and the Laurentide goes 0.17 -> 1.72 -> 0.26 Mkm2. No sheet
survives a warm precession phase, so none grows big enough to advance to 40 N or fill Hudson Bay. The
snow, degree-day and refreezing physics of the mass balance are standard (section 1). The measured causes,
ranked:

1. **A margin cell melts as if all of it were its outermost 10 km.** Its balance is taken at `edge_h`
   ~400 m. That is the Nye profile 10 km in from the edge, but the profile rises to ~1350 m across a ~110 km
   cell (mean ~900 m). This is the biggest single lever: -45 -> -98 m. It is shared with the run's margins
   (`earth.ICE_EDGE_M` = `icemass.EDGE_H`), so changing the zoom alone breaks the unforced-start consistency
   test (-17 -> -46 m in 20 kyr, bar 25 m).
2. **The orbit's summer response is ~3x Earth's.** `insol_k` is 0.25 C per W/m2. Both the model's own
   seasons and the observed ones imply 0.08-0.09 C per W/m2 at 40-70 N, and GCM Eemian and 116 ka runs give
   ~0.05-0.1. Precession swings land summers by about +-10 C, so it nucleates ice easily at a cold phase and
   destroys it half a cycle later. With `insol_k` 0.10 the zoom gets *deeper*: -45 -> -62 m, with 6 endings.
   The rule is shared with the run (`icemass.INSOL_K`).
3. **The base climate's North Atlantic (Q7).** The model's NH overturning sinks only 4.1 Sv, and it sinks in
   Baffin Bay (75 N, 63 W). The Norwegian Sea is 0.5 C and freezes in winter (real ~7-8 C, ice-free).
   Fennoscandia's January is 18 C too cold and its July 5 C too cold. Its ice in the zoom is a cold-bias
   artefact, and the observed baseline removes it. Labrador's +5.5 C summer is *not* ocean heat: the sea
   beside it is close to the observed temperature.
4. **Eastern Canada's winter precipitation is about half the observed**, and its summer rain almost double.
   Labrador's snowfall is 236 mm w.e./yr against 408 on the observed climate; the Hudson Bay lowlands get 108
   against 271. Combined with the +5..+6 C summers, this keeps Labrador from nucleating.
5. **Smaller:** PW-448's "Keewatin needs ~-9 C" came from a probe orbit that isn't glacial for the kernel's
   summer (section 2). The cycle's summer-sun metric is half a month later than the kernel's warm month.

Not causes: Hudson Bay (ice grounds across all of it once the sheets around it are big), the front's
advance rate (~180 m/yr when the balance allows), and the degree-day factors.

All numbers are Earth L6, 600 kyr, in memory, on main at fc0cd0b with PW-450's vegetation. That gives a
minimum of -45.1 m at 314 kyr, the same as the showcase 098d5d. The scripts are in the session scratchpad
`pw033/`: `probe1.py` (regional bare-ground year), `orb.py`, `zdiag.py` / `zstat.py` (an instrumented zoom),
`ocean.py`, `seasonk.py`, `consist.py` and `hb.py`.

## 1. Inception (Q1): snowfall, degree-day factors, melt season

These are bare-ground years over ice-free land boxes at today's orbit and dTg 0, from `probe1.py`. It uses a
numpy copy of `climate_melt` that reproduces the kernel's SMB exactly. "obs base" is `baseline=obs`.

| region | obs Tjul / model | obs Tjan / model | obs P / model (mm) | model Pjul : Pjan rate | snowfall model / obs base (mm w.e.) | melt months >0 C model / obs base | PDD model / obs base |
|---|---|---|---|---|---|---|---|
| Keewatin 58-68 N | 11.8 / 13.8 | -29.7 / -26.7 | 295 / 421 | 610 : 232 | 174 / 149 | 4.7 / 4.5 | 1349 / 1078 |
| Baffin | 3.2 / 5.4 | -32.6 / -30.7 | 324 / 427 | 342 : 512 | 345 / 252 | 2.8 / 2.1 | 468 / 295 |
| Labrador 50-60 N | 11.9 / **17.9** | -21.0 / -17.7 | 784 / 1065 | **1762 : 368** (obs 906 : 662) | **236 / 408** | 6.1 / 5.0 | 2160 / 1163 |
| Hudson Bay lowlands | 15.4 / **21.1** | -20.9 / -15.5 | 622 / 890 | **1569 : 211** (obs 820 : 424) | **108 / 271** | 6.8 / 5.0 | 2743 / 1646 |
| Fennoscandia | 14.2 / **9.1** | -8.7 / **-26.8** | 718 / 459 | 542 : 376 | 275 / 262 | 4.0 / 7.2 | 858 / 2037 |
| N Siberia 65-77 N | 11.5 / 10.5 | -28.2 / -31.9 | 330 / 249 | 403 : 95 | 113 / 161 | 4.0 / 4.5 | 930 / 1078 |
| Alaska | 10.4 / 8.4 | -19.3 / -30.4 | 452 / 438 | 622 : 254 | 245 / 224 | 3.7 / 4.8 | 724 / 1107 |

- **Degree-day factors and refreezing are standard.** `ddf_snow` 3 and `ddf_ice` 8 mm w.e. per PDD are
  Braithwaite 1995's values. Refreezing 0.6 of the snowmelt matches Reeh 1991's 60% cap when the year's snow
  all melts. With these, bare ground goes positive when PDD < ~0.41 x snowfall (3.27 snow - 8 PDD > 0). For
  Keewatin's 175 mm that is PDD < ~70, a warmest month of ~+1 C. This agrees with Ohmura et al. 1992's
  equilibrium-line summer temperature: JJA ~-1.5 C at 200 mm, -0.9 C at 400 mm. The melt seasons (4-5 months
  above 0 C in Keewatin) are like the observed (Baker Lake: Jun-Sep).
- `pdd_sigma` 5 C is Reeh's Greenland value. Summer day-to-day spreads measured in the Arctic are ~2.5-3.5 C
  (e.g. Fausto et al. 2009), so 5 C adds melt in months whose mean is near 0. This is a refinement, not a
  cause measured here.
- **Snowfall.** Keewatin and Baffin get as much snow as on the observed climate, or more. Labrador and the
  Hudson Bay lowlands get half to 40%, because the model rains 4.8-7.4x more per month in Apr-Sep than in
  Oct-Mar (observed 1.4-1.9x) and its summers are 5.5-5.7 C too warm. Real Labrador-Ungava, a core
  Laurentide inception area with ~300-450 mm w.e. of snow, is the region the model misses most.

## 2. The interior's summers at a glacial orbit (Q2)

**The orbit PW-448 probed isn't a glacial orbit for the mass balance.** PW-448 picked the series' minimum of
the frames' "65 N July" metric, months 3-4 raw (Jun 21 - Aug 21). That is t=592 kyr, with perihelion 356 deg.
At that orbit May-June gain +28 / +10 W/m2 while Jul-Sep lose up to -40. The kernel's warmest month feels
the sun of months 2-3 (lagged, centred on the solstice), which is only -6.5 W/m2 at t=592. That is why the
warmest month came out *warmer* than today's. The coldest orbit for the kernel is t=309.5 kyr (obliquity
22.3, e 0.049, perihelion 254 deg; -43.9 W/m2), which is where the zoom's deepest glacial is (314 kyr). The
two metrics correlate at only 0.57 over the series.

July temperature and the share of bare land with positive balance, at that orbit (`MET=kern`):

| region | today, dTg 0 | glacial orbit, dTg 0 | dTg -3 | dTg -6 | obs base, dTg -3 | obs base, dTg -6 |
|---|---|---|---|---|---|---|
| Keewatin | 13.8 C, 0% | 7.7, 1% | 3.9, 7% | 0.4, 24% | 2.0, 9% | -1.5, 22% |
| Baffin | 5.4, 11% | 0.9, 27% | -2.4, 75% | -5.5, 100% | -4.9, 100% | -8.1, 100% |
| Labrador | 17.9, 0% | 12.0, 0% | 8.6, 1% | 5.2, 4% | 3.3, 5% | -0.1, **68%** |
| Hudson lowlands | 21.1, 0% | 14.6, 0% | 11.4, 0% | 8.4, 0% | 6.1, 0% | 3.2, 4% |
| Fennoscandia | 9.1, 3% | 3.9, 14% | 0.2, 36% | -3.0, 64% | 7.4, 2% | 3.2, 16% |
| N Siberia | 10.5, 1% | 4.3, 4% | 0.4, 17% | -2.9, 45% | 1.7, 9% | -1.6, 40% |
| Alaska | 8.4, 2% | 3.0, 12% | -0.6, 44% | -3.8, 73% | 1.8, 10% | -1.5, 36% |

- PW-448's "Keewatin needs dTg ~-9 C, Labrador ~-11 C" was an artefact of that orbit. At the real cold orbit
  the orbit alone cools Keewatin's July by 6.1 C, and Keewatin and Baffin nucleate at dTg -3. On the observed
  baseline Labrador nucleates at about -6.
- **Continental summer cooling is not damped.** Per C of dTg, July and January cool alike: Keewatin
  1.4 / 1.3 C per C, Labrador 1.3 / 1.3, which is the 0.5-1.5 polar amplification. Real LGM interiors near
  the sheets cooled more in summer (the sheets' own air), and the model has that as `air_mass` once a sheet
  exists. The 11-15 C glacial Julys PW-448 saw were the wrong orbit plus the +2..+6 C base bias.

## 3. Why the ice prefers 70-80 N (Q3)

It's the temperature, not the moisture. At the cold orbit and dTg -3, Siberia's snowfall (151 mm) is less
than half Labrador's (341), yet 17% of Siberia nucleates against 1% of Labrador. Siberia's, Alaska's and
Fennoscandia's July is 0-1 C; Labrador's is 8.6 C. The model's base-climate bias has the sign pattern
"North America too warm (Keewatin +2.0, Baffin +2.2, Labrador +6.0, Hudson +5.7 C in July), Eurasia and
Alaska too cold (Fennoscandia -5.1, Alaska -2.0, N Siberia -1.0 in July; January -18 / -11 / -4)". So at
any cooling the first snowfields are Eurasian, Alaskan and on the Arctic islands. Real Siberia stayed
ice-free because it was dry *and* its summers were warm, and the model's is too dry already (249 vs 330 mm).

## 4. How ice spreads (Q4)

From an instrumented zoom (`zdiag.py`), per step and region: ice area, the southmost ice, the margin's and
the front's balance, and the share of front cells with positive balance.
- **The advance is fine when the balance allows it.** From 306 to 313 kyr, 70-100% of the front cells have
  positive balance and the Laurentide's margin goes 62 -> 54 N in ~5 kyr, ~180 m/yr (real advances
  ~50-300 m/yr). The height feedback works inside the sheet: Keewatin's ice reaches 1.0-1.5 km.
- **Nothing survives the warm half-cycle.** From 315 to 322 kyr the margins run at -1 to -5 m/yr and the
  fronts at -3 to -6. The ~1-1.5 km Keewatin and Labrador ice is gone in ~8 kyr. Over 600 kyr the Laurentide
  is never above 2 Mkm2 (it peaks at 1.7). Every glacial is a heartbeat (PW-440's word).
- **The margin rule is the lever.** A margin cell's surface is capped at `edge_h` = 408 m, the Nye profile
  (75 kPa) 10 km in. Across a whole ~110 km cell the profile rises to 1354 m. The cell's area-mean surface is
  2/3 of that, ~900 m: ~3 C colder than the cap, at 6.5 C/km. The cell's ice melts as if it were all its
  outermost 10 km (PW-115: the ablation zone is one cell wide). Sensitivity:

| variant (600 kyr) | min sea level | dTg at min | interglacial ice % of land | Laurentide at min, Mkm2 / south | Laurentide max / southmost ever | time Laurentide > 2 Mkm2 | Fennoscandia at min | endings, backstops |
|---|---|---|---|---|---|---|---|---|
| main (= 098d5d) | -45.1 @ 314 | -1.93 | 8.7-9.8 | 1.63 / 54.9 N | 1.68 / 53.9 | 0% | 1.53 / 54.4 | 2, 0 |
| margin and front 900 m (`edge_h=900`) | **-97.7** @ 478 | -3.40 | 9.7-13.3 | 2.04 / 54.9 | 2.51 / 50.5 | 5% | 2.74 / 53.2 | 5, 0 |
| margins only 900 m | -65.3 | -2.59 | 9.4-11.1 | 1.80 / 54.7 | 1.80 / 53.7 | 0% | 1.77 / 54.2 | 5, 0 |
| fronts only 900 m | -72.9 | -2.83 | 9.1-12.2 | 2.04 / 55.0 | 2.53 / 50.5 | 3% | 2.29 / 52.6 | 5, 0 |
| `insol_k=0.10` | -62.3 | -2.59 | 11.8-13.0 | 1.53 / 56.7 | 1.54 / 54.9 | 0% | 1.38 / 54.7 | 6, 0 |
| `baseline=obs` | -31.0 | -1.64 | 8.8-10.3 | 2.48 / 53.9 | 3.16 / 49.5 | 9% | 0 | 2, 2 |
| obs + `edge_h=900` | -71.3 | -2.84 | 9.6-14.0 | **5.02 / 46.6** | 5.07 / 45.9 | 60% | 0.75 / 58.5 | 5, 0 |
| obs + 900 + `insol_k=0.10` | -70.6 | -2.86 | 12.6-14.6 | 4.93 / 46.7 | 4.90 / 45.9 | 96% | 0.72 / 58.5 | 7, 0 |

  (Laurentide = 100-60 W, 35-75 N; Fennoscandia = 0-40 E, 50-72 N. Interglacial ice is the share of land at
  the highest 5% of sea levels after 50 kyr, the bar being ~8-9%.)
- With the observed baseline and real-sized margins, the Laurentide reaches 5 Mkm2 and 46.6 N and holds more
  than 2 Mkm2 for 60% of the time. That is the first LGM-like geography any variant gave. But the
  interglacials keep too much ice (9.6-14%), and Siberia still holds 5 Mkm2.
- **It can't be changed in the zoom alone.** The run's margins use the same 408 m (`earth.ICE_EDGE_M`). With
  `edge_h=900` the unforced cold moment of `tests/test_timezoom_consistency.py` drifts -46 m in 20 kyr
  (main -17, bar 25). The run's sheets are this rule's equilibrium at 408 m. A sub-cell margin (PW-115) has
  to go in both, and then the run's cold-era seeds need re-checking, after PW-422's history of margins
  creeping onto warm land.

## 5. The observed baseline (Q5)

These are the bias fields (observed - model) at the start; temperatures in C, precipitation as a ratio.

| region | Tjul | Tjan | Pjul x | Pjan x |
|---|---|---|---|---|
| Keewatin | -2.0 | -3.0 | 0.76 | 0.93 |
| Baffin | -2.7 | -1.9 | 1.22 | 0.51 |
| Labrador | **-6.0** | -3.4 | 0.54 | **1.87** |
| Hudson lowlands | -5.7 | -5.5 | 0.53 | 2.07 |
| Fennoscandia | **+5.0** | **+18.1** | 1.63 | 1.97 |
| N Siberia | +1.0 | +3.7 | 1.10 | 3.49 |
| Alaska | +1.9 | +11.2 | 0.94 | 1.22 |

It cools and wets Canada, where the Laurentide grows: 1.6 -> 2.5 Mkm2, reaching 49.5 N at its maximum. But
it warms Eurasia and Alaska by +1..+5 C in summer and removes Fennoscandia's 1.5 Mkm2 and half of Siberia's
and Alaska's ice. The model's depth came mostly from the cold-biased Eurasian ice, so the more realistic
geography is shallower (-31 m). The observed Fennoscandia is warm because of the North Atlantic Drift
(section 7). Its sheet needs a colder orbit and global state than the model's -1.6 C reaches.

## 6. Hudson Bay (Q6)

At L6 the bay is 76 sea cells (0.89 Mkm2), with a mean depth of 103 m and a maximum of 236. Ice floating
there needs > 1.12 x the depth (~115 m) to ground, and a front facing open water calves at ~100 m/yr. Once
the sheets around the bay are big enough, ice grounds across all of it: 0.89 Mkm2 in obs + 900 m, with a
mean of 0.53 Mkm2 while the Laurentide is > 3 Mkm2. On main the most is 0.06. **The bay is not a cause:**
it fills when the sheets that should fill it exist.

## 7. The overturning (Q7)

### The real world (literature)
- **The LGM AMOC was shallower, and its strength is debated.** Glacial North Atlantic Intermediate Water
  filled the upper ~2 km, and southern-source water filled the deep Atlantic below (Curry & Oppo 2005;
  Lynch-Stieglitz et al. 2007). The 231Pa/230Th data allow a near-modern or modestly weaker LGM rate, with
  near-collapse only in Heinrich Stadial 1 (McManus et al. 2004).
- **Sea ice and the polar front were further south.** In winter the sea ice reached ~45-50 N in the western
  North Atlantic and the polar front sat at ~42-45 N (CLIMAP 1981; MARGO 2009; de Vernal et al. 2005).
  The eastern Nordic Seas were seasonally ice-free in summer, an open-water moisture source for the
  Fennoscandian and Barents sheets (Hebbeln et al. 1994).
- **The heat goes north-east.** Today the Gulf Stream and North Atlantic Drift take ~0.5 PW past 50 N into
  the Norwegian Sea. That is why Norway's coast is 10-20 C warmer in winter than Labrador at the same
  latitude (Seager et al. 2002 attribute much of the zonal winter contrast to the atmosphere's stationary
  waves as well). Labrador sits on the cold Labrador Current. This is the origin of Earth's "Labrador cold,
  Fennoscandia warm" contrast.
- **Inception: moisture against cooling.** In the last glacial inception (~116 ka) the North Atlantic stayed
  warm while the continents cooled. Ruddiman & McIntyre 1979/1981's "warm ocean, cold continent" supplied the
  moisture for the growing sheets, and in GCMs the inception is helped by the poleward moisture flux from
  warm low-latitude seas (Khodri et al. 2001). A weaker AMOC cools winters far more than summers (sea ice),
  and summer melt is what controls inception, so it helps little and costs snowfall. AMOC weakening is
  usually a deglacial and stadial player (Ganopolski & Rahmstorf 2001), not an inception driver.

### Our simulation (`ocean.py`, Earth L6 today's surface, `climate.compute`)
There is an overturning term (`ocean.solve`: salinity -> density -> sinking -> a warm inflow that heats
the SST: `moc_heat`). It feels the time zoom's meltwater (`melt`, PW-018: ~0.03 Sv on Earth, and no memory
between refreshes) and its cooling.

| | dT 0 | dT -3 | dT -6 | dT 0 + 0.1 Sv hosing (50-70 N, 60 W-0) | + 0.3 Sv | Earth (obs / literature) |
|---|---|---|---|---|---|---|
| NH sinking (Sv) | **4.1** | 6.5 | 0.3 | 2.3 | 0.2 | ~15-20 (AMOC) |
| main sinking sites | **75 N 63 W (Baffin Bay)** | 62-63 N 14-28 W (Iceland-Irminger) | 60 N 165 E (Bering) | Baffin Bay | N Baffin Bay | Nordic Seas, Labrador and Irminger Seas |
| Norwegian Sea SST annual / Jan (C) | **0.5 / -1.8** | -0.9 / -1.8 | -1.5 / -1.8 | 0.6 / -1.8 | 0.9 / -1.8 | ~7-8 / ~6 |
| `moc_heat` there (C) | -0.4 | 0.0 | 0 | -0.3 | 0 | (the NAD's warmth) |
| Irminger Sea SST / moc_heat | 4.1 / **+3.0** | 2.5 / +3.8 | -1.8 / 0 | 2.8 / +1.6 | 1.2 / +0.1 | ~6-7 |
| Labrador Sea SST / moc_heat | 2.8 / +1.1 | -0.3 / +0.7 | -1.8 / 0 | 2.1 / +0.4 | 1.7 / 0 | ~3-4 |
| Barents Sea SST | -1.8 | -1.8 | -1.8 | -1.8 | -1.8 | ~2-5 (south) |
| NAD 42-52 N, 40-15 W SST / moc_heat | 11.5 / +1.5 | 9.6 / +2.6 | 4.2 / 0 | 10.7 / +0.7 | 10.0 / 0 | ~13-15 |
| Gulf Stream 35-42 N SST | 19.6 | 17.8 | 14.2 | 19.3 | 18.6 | ~22-24 |
| Atlantic `moc_heat`, zonal mean at 50 / 60 / 70 N | +1.2 / +1.2 / +0.4 | +1.7 / +1.7 / +0.3 | 0 | +0.6 / +0.6 / +0.2 | 0 | |
| Fennoscandia Tjul / Tjan (obs 14.2 / -8.7) | 9.3 / **-26.7** | 5.6 / -30.7 | 2.3 / -34.6 | 9.5 / -26.7 | 9.7 / -26.4 | |
| British Isles Tjan (obs +4.5) | **-3.4** | -14.5 | -22.6 | -3.1 | -2.7 | |
| Labrador Tjul / Tjan (obs 11.9 / -21.0) | 17.4 / -17.9 | 13.9 / -22.1 | 10.7 / -26.2 | 17.4 / -17.5 | 17.4 / -17.1 | |

- **The North Atlantic Drift never reaches Norway.** The model's overturning warms the Irminger and Labrador
  side by +1..+3 C and the Norwegian Sea by nothing. The Norwegian and Barents seas freeze every winter, so
  Fennoscandia gets a continental winter (-27 C against -9 observed). Its summer is 5 C too cold as well, and
  its precipitation is 64% of the observed. **Fennoscandia's cold bias is an ocean heat-transport signature**
  (the missing NAD, sinking in Baffin Bay instead of the Nordic Seas), and it is why the model's Eurasian
  ice grows where Earth's didn't, and why Fennoscandia's ice vanishes on the observed baseline.
- **Labrador's warm bias is not.** Labrador's sea is close to the observed (2.8 C, moc_heat +1.1), and its
  bias is a summer one (+5.5 C, with January +3). Hosing the overturning off leaves it unchanged (17.4 C).
  It is a land-summer and continentality bias of the base climate (with the summer rain, section 1).
- **Response.** Under -3 C the sinking moves south to Iceland-Irminger and strengthens to 6.5 Sv: an
  LGM-like southward shift. Under -6 C it collapses to 0.3 Sv, which is further than the LGM's shallower but
  active cell. It is very sensitive to fresh water (0.3 Sv shuts it). In the time zoom it barely matters:
  the glacials reach only ~-2 C, the meltwater is ~0.03 Sv, and the effect on land (Fennoscandia +-0.3 C) is
  small next to the base bias.
- So the overturning plays a part through the base climate: it puts Earth's ice in the wrong places (rank 3).
  It is not a lever inside the time zoom's dynamics. Fixing it is a climate-model job (ocean, high impact,
  shared by everything), not a time-zoom fix.

## 8. The orbit's response coefficient (`insol_k`)

The model's own seasonal cycle on ice-free land (`seasonk.py`) gives the July-January temperature range per
range of the lagged top-of-atmosphere sun:

| lat | sun range (W/m2) | model range (C) -> C per W/m2 | observed range -> C per W/m2 |
|---|---|---|---|
| 40 | 316 | 26.4 -> 0.083 | 27.7 -> 0.088 |
| 50 | 383 | 31.4 -> 0.082 | 31.5 -> 0.082 |
| 60 | 437 | 38.1 -> 0.087 | 33.9 -> 0.078 |
| 65 | 459 | 41.1 -> 0.090 | 36.7 -> 0.080 |
| 70 | 475 | 40.4 -> 0.085 | 37.0 -> 0.078 |

Precession changes the same annual harmonic of the sun, so a linear land surface should respond to it as it
does to the seasons. That is ~0.08-0.09, and GCMs give ~0.05-0.1 for Eemian and 116 ka summers (Arctic land
+2..+5 C for ~+50-60 W/m2; Otto-Bliesner et al. 2013, CAPE 2006). The zoom uses 0.25, ~3x more, and the
run's cycle-averaged balance uses the same `icemass.INSOL_K`. Its history is a 65 N calibration
(PW-398: "a mid-latitude land sensitivity"; PW-034/PW-114: above 0.3 the Eemian start melts Antarctica and
Greenland; PW-440: 0.45 gave cycles but melted interglacial Antarctica). With 0.10 the Earth zoom gets
deeper (-62 m, 6 endings), because the warm half-cycles stop erasing the ice. The interglacials keep more
ice, though (11.8-13% of land, bar 8-9), and the Laurentide's geography doesn't change. It is a shared
constant with a long calibration history, so it is a decision, not a fix.

## 9. Ranked causes and what was done

| rank | cause | measured lever | owner | done here |
|---|---|---|---|---|
| 1 | a margin cell's balance at its outermost 10 km (`edge_h` 408 m vs the cell's ~900 m mean) | -45 -> -98 m; with obs: Laurentide 5 Mkm2 to 46.6 N | time zoom **and** run (shared `ICE_EDGE_M`) | needs-decision draft (consistency test fails if the zoom alone changes) |
| 2 | orbit response 3x the seasonal one (`insol_k` 0.25 vs 0.08-0.09) | 0.10: -62 m, 6 endings, interglacial ice up | shared `icemass.INSOL_K` | needs-decision draft |
| 3 | North Atlantic overturning sinks in Baffin Bay (4 Sv); Nordic Seas frozen; Fennoscandia -18 C in Jan | Fennoscandia's and Eurasia's ice are a cold-bias artefact | climate / ocean | draft |
| 4 | E Canada: winter precipitation ~0.5x, summer ~1.9x observed; summer +5.5 C | Labrador snowfall 236 vs 408 mm | climate | draft |
| 5 | the cycle's summer metric (Jun 21-Aug 21 sun) is half a month after the kernel's warm month (May 21-Jul 21); PW-448's probe orbit | corr 0.57; PW-448's -9 C needed is really ~-3 to -6 | time zoom | draft (low); PW-448 Update |

**No fix is merged.** Every lever the numbers show is in code shared with the run or the base climate. Each
one alone either breaks the unforced-start consistency (margins) or lifts the interglacial ice above the
8-9% bar (margins, `insol_k`). The rule for this ticket is "a large judgement call goes to a decision", and
these are. The likely good combination is a sub-cell margin in both the run and the zoom, plus `insol_k`
from the seasonal response, plus the observed baseline for Earth. It needs the run's 10-seed cold-era check
and a re-balance of the interglacials, which is a joint decision (drafts `draft-subcell-margin-run-and-zoom.md` and `draft-orbit-response-from-seasons.md`).

## Sources
- Braithwaite 1995 (J. Glaciol. 41): degree-day factors ~3 (snow), ~8 (ice) mm w.e. per PDD. Reeh 1991
  (Polarforschung 59): the PDD model, sigma 5 C, 60% retention. Fausto et al. 2009 (J. Glaciol. 55): summer
  sigma ~2.5-3.5 C. Ohmura et al. 1992 (J. Glaciol. 38): ELA summer temperature vs accumulation.
- Curry & Oppo 2005 (Paleoceanography 20); Lynch-Stieglitz et al. 2007 (Science 316); McManus et al. 2004
  (Nature 428); MARGO Project Members 2009 (Nat. Geosci. 2); de Vernal et al. 2005 (QSR 24); Hebbeln et
  al. 1994 (Nature 370); Seager et al. 2002 (QJRMS 128); Ruddiman & McIntyre 1981 (Science 212); Khodri et
  al. 2001 (Nature 410); Ganopolski & Rahmstorf 2001 (Nature 409).
- Otto-Bliesner et al. 2013 (Clim. Past 9) and CAPE Last Interglacial Project Members 2006 (QSR 25): Eemian
  Arctic summer warming.
