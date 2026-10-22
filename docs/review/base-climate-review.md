# Base climate and whole-sim behaviour: a review for v2

2026-10-22, base-climate lane, phase 1 (written review: no model defaults changed). Main 3798b6a.

Sources: `planet/climate.py`, `planet/ocean.py`, `planet/tectonics/earth.py`, `planet/icemass.py`; the ice v2 lane
(`docs/review/ice-v2-review.md`, `ice-v2-criteria.md`, `ice-v2/checkpoint-0.md`, `ice-v2/stage-1.md`); the climate
and ocean tickets (PW-015, 026, 038, 039, 346, 352, 457, 458, 558, 559, 563, 564, 566..569).

Measured for this review (about 10 minutes of compute in all):
- `tools/earth_check.py` at L6 on today's Earth.
- New `tools/climate_bias.py` (committed): biases where ice grows, plus four mechanism checks that work on any
  geography. It takes ~15 s at L6. Run at dT 0 and dT −6, plus one test with `evap_cool` raised.
- An Earth-only bisect of the overturning over five revisions of `planet/` (each a fixed-geography climate, ~8 s).
- The thermostat, read from the 15 existing L6 1 Gyr `tools/ice_diag.py` runs of the ice lane (10 from checkpoint 0,
  5 on the new main). No new runs.

Earth is used as a known point, not a target. Every bar below is a plausibility range, and "done" means the
mechanism is right and the numbers are believable, not that they match.

## Summary for the owner

**The headline.** Most of the climate biases that bother the ice come from four mechanisms, and fixing them is honest
physics, not tuning. I've ranked them by how much they move the ice.

1. **The North Atlantic's deep-water sinking is in the wrong place** (it sinks in Baffin Bay, not the Nordic Seas).
   - The Norwegian Sea then freezes. Fennoscandia's winters run 16–19 C too cold and its summers 4–5 C too cold.
     Iceland and Svalbard are 17–27 C too cold in winter.
   - This is the main reason **Eurasia runs cold** and grows ice caps at today's climate.
   - It is a regression. The bisect pins it on one commit, PW-015 stage 1's new rain kernel (1416523, 10-16). Before
     it, Earth sank 11 Sv in the Greenland Sea. After it, 4.9 Sv sinks in Baffin Bay. (Earth: ~15–17 Sv, Nordic and
     Labrador seas.)
2. **The air over the sea only knows its own water.** A sea cell's air comes from its sea temperature and its latitude,
   never from the wind blowing off the land beside it. Sea ice likewise comes from the latitude, not from the cold air
   flowing over the water.
   - So Hudson Bay, Baffin Bay and the Sea of Okhotsk stay open all winter. Hudson Bay's coldest month is −5 C against
     the observed −28 C.
   - The pack ice around Antarctica is 9 C too warm in winter, and the southern winter sea ice is ~25% too small.
   - This is a big part of why **North America runs warm**: Labrador and the Hudson Bay lowlands are 3.5–5.5 C too
     warm in winter.
3. **Summer heat on land isn't limited by clouds and evaporation.** The land's summer warmth is set by latitude and
   distance from the sea, with only a ±1.5 C wet/dry correction.
   - Humid east coasts and interiors run 3–6 C too warm in summer: Labrador +4.7, the Hudson Bay lowlands +5.7, the
     Great Lakes +5.9, SE China and the SE USA +4–5.
   - Small lands in windy southern oceans get a big continent's seasons. Southern Hemisphere coasts have 1.7× the
     observed seasonal range and summers 4–6 C too warm.
   - This is the other part of **North America too warm, so glacials too shallow**. Laurentide inception needs cool
     Labrador summers.
4. **The CO2 thermostat hardly answers the temperature.**
   - Measured on 15 runs, a 1 C cooling raises the CO2 warming by only 0.14 C (median; range 0.06–0.38). The rule as
     written should give ~0.7 C.
   - Weathering here is physical erosion times a temperature factor. Erosion (mountains, sea-level falls cutting
     rivers deeper) most likely swamps the temperature factor (not yet separated).
   - So the random climate drift passes into the temperature almost unopposed (0.55–1.05 of it). The CO2 term mostly
     tracks volcanic output, which makes it a forcing rather than a brake.
   - That, plus "normal" being today's ice-age Earth (PW-559), is why **default planets spend 36–100% of their time
     in an icehouse** (median ~62%; Earth ~10–30%).

**Pushback on one part of the brief.** The cold summers on the Greenland and Arctic Canada *margins* aren't the base
climate.
- The base climate's bare land there is 1–3 C *too warm* in summer: Greenland's ice-free rim +1.8, Baffin +2.7, the
  Arctic islands +1.0.
- The cold comes from the ice-surface rules on top (ice_cool, the summer damping, the carried sheet air: PW-569,
  PW-439). Greenland's ice surface is −4.3 C in summer.
- That stays with the ice lane. Base-climate fixes won't warm those margins. Fixing the overturning (item 1) will even
  cool the Labrador Sea side a little.

**What I'd not expect base-climate fixes to do.**
- They move *where* ice grows and *how deep* glacials go (more Laurentide, less Scandinavia at dT 0). They should also
  shrink the icehouse share.
- The L4 endings test (PW-568) runs on a generated planet, and the same moment deglaciates once the carried air is off.
  So I expect that test to hinge on the ice-surface air more than on items 1–3. Item 4 doesn't touch a 100 kyr zoom at
  all.
- I'd make that an explicit check after stage 2, not an assumption (section 4).

**Where to stop.** Once the ice-relevant regions' summers are within about ±3 C and their winters within about ±6 C,
the sinking is in open polar seas at a plausible strength, and the icehouse share sits in 15–45% on ~70% of seeds.
Beyond that we'd be chasing Earth's particulars (Gulf Stream separation, Tibet's rain), which a made-up world doesn't
need.

**The plan's leans (section 4).**
- Stage 0: tools (mostly done).
- Stage 1: the overturning, PW-458.
- Stage 2: the sea's air and the sea ice, PW-346 broadened.
- Stage 3: summer heat, PW-352/457, plus small-land seasons.
- Stage 4: the thermostat, then the set point (PW-559), then stellar brightening (PW-564), in that order.
- Then hand the ice lane's honest zoom rules their test.
- A replacement of the fixed Earth temperature curve by a simple energy balance stays a later research option.
- Stages 1–3 are ~1–2 agent-days each. Stage 4 is ~2–3 days with the 10-seed checks.

## 1. Where the climate is implausible against Earth, and why

### 1.1 How the temperature is made (one paragraph)
- The model doesn't solve an energy balance (criteria A1). It starts from **a fixed Earth curve of temperature by
  latitude**: 27.8 + 0.5 dT at the equator and −10.4 + 1.5 dT at the pole, with a small tilt adjustment.
- It lowers that by 6.5 C/km of height, then gives each place a seasonal swing:
  - on land, 24 C × a latitude factor;
  - at sea, 6 C × that factor.
- The winds then carry sea air over land, and land air over land. Ocean currents move sea-surface warmth around.
- The overturning adds its inflow's warmth, but only as a redistribution within each latitude band (`moc_zonal` 1,
  PW-265).
- Rain, evaporative cooling (±1.5 C), vegetation albedo (±2 C) and the ice surface come after.
- So **geography can only move heat sideways within a latitude**. It never changes how warm a latitude is overall.
  That's a fair toy for Earth-like planets. It is also why several biases below come in pairs: too warm in one place,
  too cold in another.

### 1.2 Regional biases where ice grows (Earth L6, dT 0, against NCEP 2 m and GPCC/GPCP)

`tools/climate_bias.py`, section 1, selected rows (C; P as model/observed):

| region | summer (warmest month) | winter (coldest month) | annual | precip ratio | mechanism (section) |
|---|---|---|---|---|---|
| Labrador / Quebec N (bare) | **+4.7** | +3.6 | +3.7 | 1.41 | summer heat (1.3c); open seas (1.3b) |
| Hudson Bay lowlands | **+5.7** | +5.5 | +4.9 | 1.42 | same |
| Great Lakes / Midwest | **+5.9** | +2.6 | +3.7 | 1.70 | summer heat |
| Keewatin / Nunavut | +1.5 | +3.2 | +3.8 | 1.49 | open Hudson Bay |
| Arctic Canada islands (bare) | +1.0 | +0.5 | +2.4 | 2.17 | near right |
| Baffin Island (bare) | +2.7 | +1.9 | +1.2 | 1.31 | warm Baffin Bay (the sinking) |
| Greenland's ice-free rim | +1.8 | −5.5 | −1.6 | 0.93 | base about right in summer |
| **Greenland's ice** | **−4.3** | −14.2 | −6.3 | 0.98 | the ice-surface rules (PW-569), not the base |
| Fennoscandia | **−5.3** | **−18.5** | −10.5 | 0.62 | Nordic Seas frozen (1.3a) |
| Kola / Karelia | −4.1 | −15.9 | −8.6 | 0.64 | same |
| Iceland | −1.9 | **−26.6** | −13.1 | 0.34 | same, plus dry storm tracks |
| Svalbard / Franz Josef | −1.9 | −17.2 | −8.9 | 1.02 | same |
| Alaska / Yukon | −1.2 | **−12.0** | −4.6 | 1.04 | winter sea air doesn't reach inland (PW-026) |
| Tibet | −2.9 | −5.4 | −3.8 | 0.24 | dry plateau (PW-353) |
| Patagonia | **+6.4** | −2.6 | +1.9 | 1.16 | small land, big-continent seasons (1.3d) |
| Antarctic coast ice (< 1500 m) | +1.2 | −7.6 | −0.3 | | |
| Antarctic plateau (> 2500 m) | +2.0 | +3.2 | **+9.0** | | annual mean from two months (1.3f) |
| Southern Ocean 60–70S | +4.6 | **+8.7** | +5.9 | 0.45 | the sea's own air (1.3b; PW-346) |
| Labrador Sea / Baffin Bay | +0.8 | **+11.0** | +4.6 | 0.38 | the sinking is here (1.3a) |
| Nordic Seas | −3.6 | **−9.5** | −6.0 | 0.31 | no North Atlantic Drift (1.3a) |
| Barents Sea | −3.3 | −8.0 | −6.1 | 0.37 | same |

The biases match the ice lane's findings: Labrador July +5.5..6 (PW-033/457), Fennoscandia January −18 (PW-458),
the dT-0 caps in Eurasia's mountains (stage 1c), and Antarctica's annual warmth (PW-039).

### 1.3 The mechanisms

**(a) The overturning sinks in Baffin Bay (PW-458, PW-016). The biggest single cause.**
- Today the model's only northern sinking site is at 67N 51W (4.9 Sv, 0.42 PW). The overturning's warmth then goes
  into Baffin Bay and the Labrador Sea: Baffin Bay's winter is +17 C too warm.
- `moc_zonal` takes the band's mean back off, so the Norwegian coast is *cooled* (−0.9 C). Its sea is −0.1 C annual
  against +6.8, and −5.8 in winter against +3.5. The Nordic and Barents seas freeze.
- Bisect on Earth's fixed geography (the climate alone, ~8 s per revision):

  | revision | NH sinking | where | Norwegian coast sea air, annual / winter |
  |---|---|---|---|
  | e4c341a (10-16) | 10.2 Sv | 72N 28W (Greenland Sea) | +2.4 / −3.3 |
  | cdd867d (10-16, overturning to a steady state) | 11.3 Sv | 72N 27W | +3.0 / −2.7 |
  | **1416523 (PW-015 stage 1, rain kernel)** | **4.9 Sv** | **67N 51W (Baffin)** | −0.1 / −5.8 |
  | 7fbf3b6 (10-19), main | 4.9 Sv | 67N 51W | −0.1 / −5.8 |

- So the rain kernel's new moisture transport flipped the sinking. The likely path: salinity. The high-latitude seas'
  rain is now a third of the observed (Nordic Seas ×0.31), so it isn't extra rain at sea. Suspects are the rivers, the
  ice export and the brine terms that set which polar sea is densest. That needs a factor separation in `ocean.py`'s
  budget.
- Even before the flip, the Norwegian coast was ~4 C too cold. The North Atlantic Drift reaching only ~55N is a
  second, older cause (PW-458's "why no NAD past 55N"; PW-041's separation latitude).
- For made-up worlds, the general rule is that deep water should form in **open** polar seas with a warm inflow. It
  shouldn't form in a semi-enclosed bay because the bay freezes hardest. That bar can be checked on any planet.

**(b) The air over the sea only knows its own water (PW-346, broadened).**
- In `_air_temps` the land's air is carried by the wind (`carry`), but a sea cell's air is pinned to its own water
  (k = 0 at sea).
- A sea cell gets the sea-ice inversion only where *the latitude's* annual sea would be below freezing (`frozen` from
  `sea_temperature`). An enclosed or leeward sea at 55–65N never gets the continent's winter air, and never freezes
  over in winter:

  | sea | model winter air | observed | model annual |
  |---|---|---|---|
  | Hudson Bay | −5.2 | −28.2 | 0.0 (obs −8.3) |
  | Sea of Okhotsk | −0.4 | −11.8 | 4.5 (obs 0.6) |
  | Baffin Bay | −11.9 | −29.5 | −4.1 (obs −11.7) |
  | Southern Ocean 60–70S | −5.8 | −14.5 | −0.2 (obs −6.1) |

- The winter sea-ice proxy (sea whose coldest month is below −5 C) is 15.0 Mkm2 in the north (NCEP 16.8) and 15.0 in
  the south (NCEP 20.2).
- On Earth the sea-ice edge is tilted: Labrador and Okhotsk freeze at 50–55N, while the Nordic Seas are open at 75N.
  The model's edge is set by latitude, with only the currents' SST anomalies to tilt it.
- **This is a mechanism error on any planet.** Every leeward sea, enclosed bay or sea beside an ice sheet comes out
  too warm in winter. An Antarctica-like continent's outflow never cools its own pack ice.

**(c) Summer heat on land isn't limited by clouds and evaporation (PW-352, PW-457).**
- The land's summer half-swing is 24 C × the latitude's season strength. Only the distance to the sea dilutes it
  (through the wind's carry), and `evap_cool` adds at most ±1.5 C by the summer's AET/PET. Clouds are diagnostic and
  don't shade the ground (PW-163).
- `climate_bias.py` section 4: on northern land at 35–65 deg, the summer bias goes from −2.3 C where observed summer
  rain is < 300 mm to +2.5 C where it is > 1200 mm. The wetter, the hotter: the opposite of what evaporation and cloud
  do on Earth.
- "Sea to the east" land (east coasts and lee shores, 40–65N) is +3.0 C in summer, against −2.1 C for west coasts.
- **A test of the knob, not a fix.** I raised `evap_cool` from 1.5 to 4. The humid regions came down 2–3 C (Labrador
  +2.2, Great Lakes +3.5), but the dry interiors went 2–3 C too cold. The model's summer rain in those dry regions is
  3.6× the observed (609 vs 167 mm), so the evaporation split sees wet ground there. The summer heat and the rain bias
  are tangled, so a bigger constant only moves the error around. It needs a surface energy split (PW-352's Bowen-ratio
  idea), checked with the observed rain too, so the two errors can be told apart.

**(d) Small lands get a big continent's seasons (new).**
- `climate_bias.py` section 2: in the north, the seasonal range by distance from the sea is close to the observed at
  every distance (27.5/26.4 C at the coast, 34.7/34.7 at 800–1500 km). The scheme was tuned there.
- In the south it is 16.5 vs 9.6 C at the coast and 22.2 vs 14.1 at 150–400 km, with summers +4–6 C too warm at every
  rain level. Patagonia's summer is +6.4.
- The land's own swing (24 C × season strength) doesn't depend on how big the land mass is, so a 400 km-wide land in
  the westerlies has "its own" continental air.
- On made-up worlds with many islands or narrow continents this overstates the seasons everywhere. For ice, it gives
  margins summers that are too hot.

**(e) Winter maritime air doesn't reach far inland (PW-026).** West-coast land (sea to the west, 40–65N) is 3.7 C too
cold in winter, and Alaska is 12 C too cold. This is old and known. Its effect on ice is smaller than (a)–(c): a winter
bias changes snow more than melt.

**(f) The annual mean is the midpoint of the warmest and coldest months (new, for PW-039).**
- On the Antarctic plateau the model's warmest and coldest months are only +2.0 and +3.2 C off, but its annual mean is
  +9.0 C too warm.
- Real polar interiors have a "coreless" winter: long and flat, so the annual mean sits ~6 C below the midpoint. The
  model's sine year doesn't.
- It matters little for melt, which runs on the warm months. It matters for anything that reads the annual mean:
  permafrost, ice temperature, soils, and the weathering factor. This is most of PW-039's "10 C too warm interior".

**(g) Moisture to high latitudes is about half (PW-015, PW-332).** High-latitude seas get a third to a half of the
observed rain (Nordic ×0.31, Labrador Sea ×0.38, Southern Ocean ×0.45). The southward vapour transport at 40S is half
the implied value (−0.66 vs −1.39 Sv). Meanwhile land interiors are too wet: land mean 1138 vs 791 mm, deserts ×3–12.
For ice this starves maritime margins (Iceland ×0.34, Fennoscandia ×0.62, Antarctic coasts) and over-feeds continental
ones (Labrador ×1.41, but mostly in summer, PW-457).

### 1.4 The climate's response to cooling (dT −6, the same geography)
- The fixed curve cools the poles by 1.5 × dT. On top, **the sea-ice switch is strong and abrupt**:
  - Fennoscandia's summer falls 7.5 C for a 6 C global cooling.
  - The Nordic Seas' winter falls 28 C (to −39 C).
  - The Southern Ocean's 60–70S winter falls 26 C.
  - The winter sea-ice proxy goes 15 → 25 Mkm2 in the north and 15 → 39 in the south.
- The LGM's southern winter sea ice was roughly twice today's, so the southern number is plausible. The northern one
  is dominated by the frozen Nordic Seas, which is wrong (the LGM Nordic Seas were seasonally open: Hebbeln et al.
  1994).
- Consequence: the ice sees a very non-linear climate around the dT where its nearest sea freezes. Small differences in
  dT between the run (its own dT) and the zoom (the index's cooling) then become large differences in ice. That is one
  ingredient of "the run and the zoom disagree on the ice" (the others are the two ice models and their different
  ice-surface rules, PW-567).

### 1.5 The CO2 and weathering thermostat (whole-run)

Read from the 15 existing L6 1 Gyr diagnostic runs (`ice_diag` json, after the 300 Myr spin-up; script in the
session scratch, `bc/thermo.py` and `thermo2.py`):

| measure | design (`earth.global_temperature`) | measured, median (range) |
|---|---|---|
| weathering sink's response, d ln(sink)/dT | ~0.045–0.09 per C (0.09 locally; the tropics move 0.5 × dT) | **0.020** (−0.002..0.045) |
| CO2 warming per 1 C of cooling (the feedback) | ~0.7 C | **0.14 C** (−0.12..0.38) |
| dT per C of drift | ~0.6 | **0.82** (0.53–1.05) |
| CO2 term vs dT | negative (a brake) | **positive** on 12 of 15 runs (corr up to +0.54) |
| icehouse share (ice ≥ 20 m of sea level) | | 26–100%, median ~62% (new main's 5 runs: 36–83%) |

What this says:
- **The CO2 term is a tectonic forcing, not a thermostat.** The source (spreading and arc growth) swings ×0.6–1.5
  against its baseline, and 1/`WEATHER_CO2` (2.5×) amplifies that into ±1 e-fold, ±3 C. That is real Earth-like
  behaviour (CO2 does follow tectonics). But it is in phase with warmth because it causes the warmth.
- **The brake is ~5× weaker than written.** `sim.weathered` is the bare ground's physical erosion. It grows with
  mountains, with rain, and with the base level falling under a cold era's sea-level drop (`base_rise` = the ice's sea
  level: rivers cut deeper). The likely cause is that those swamp the `exp(0.09 ΔT)` factor. That isn't separated
  yet: the diagnostics don't split the sink, which is missing tool 2.
  - Real silicate weathering is part supply-limited and part kinetically limited (West et al. 2005; Maher &
    Chamberlain 2014). The model is all supply, with kinetics as a small multiplier.
  - Plausible fixes: a weathering law with a kinetic ceiling (a regolith-residence or "weathering intensity" form), so
    extra erosion saturates while temperature and runoff stay in charge. Or count a cold era's extra rock flour as only
    weakly weathering. Either is a mechanism, not a tuned number.
- **Hysteresis and baselines.** The baselines learn over 1000 Myr (`REF_MYR`), so the run's long trends (plants
  spreading, mountains) keep the sink above its baseline. The CO2 index median is −0.2..−0.9, which leans cold
  (checkpoint 0, A3b).
- **The steady-state rule is the stock's equilibrium.** ln pCO2 = ln(source/sink)/0.4 is what dC/dt = source − sink(C,
  T) settles to. A stock (PW-558 A) changes the dynamics (how fast, and whether CO2 can pile up under ice for Myr). It
  doesn't change the steady-state strength. So PW-558 alone won't fix item 4: the sink's temperature response has to be
  fixed too.

### 1.6 The default baseline (PW-559) and stellar brightening (PW-564)
- **Baseline.** dT 0 is today's icehouse Earth, and the drift and thermostat wander around it. A default planet then
  lives in an icehouse most of the time.
  - Two separate things are bundled here: where the set point is (the climate the thermostat steers to) and how hard
    it steers (above).
  - With a working brake the drift's ±3 C spells shrink toward ±2 C, and fewer of them reach icehouse depth. So fix the
    brake before choosing an offset, or the offset gets tuned against a broken brake.
  - Lean: the set point comes from the planet's own carbon balance (outgassing against weathering at the run's start),
    not from an Earth offset. Its default should put a planet with Earth's outgassing a few C above today's Earth, like
    the Phanerozoic mean. That is PW-559's option B.
- **Brightening.** A Sun-like star brightens ~0.9% per 100 Myr: ~2.1 W/m2 of forcing per 100 Myr at Earth's albedo,
  and at the model's ~0.56 C per W/m2 (3 C per e-fold), ~1.2 C per 100 Myr.
  - Unopposed, that's ~12 C over a 1 Gyr run. With today's feedback (0.14 C/C) about 10 C. With a working one (~0.7)
    about 7 C, and more if the stock version is allowed to draw CO2 down hard, as the faint young Sun needed.
  - **So brightening must come after the thermostat**, or every long run warms by ~10 C from start to end.
  - It's planet-relative by construction: the luminosity against the run's start, from the star's age.
  - The ±3 e-fold CO2 clip would bind on 2 Gyr runs, which is another reason to do PW-558 first.

## 2. Whole-sim couplings that make it worse

| coupling | effect on the climate or ice | evidence | lean |
|---|---|---|---|
| **Rain → salinity → overturning** | a rain-kernel change flipped the sinking site (1.3a); the overturning is a switch with neighbouring states | bisect; PW-458 at −3/−6 C moves or collapses it | measure the overturning in every climate change's check (stage 0 tool) |
| **Sea level → erosion → weathering** | a cold era's sea-level fall cuts rivers deeper, raises erosion, raises the sink: CO2 falls in the cold (positive feedback) | sink response 0.02/C against 0.09; CO2 term positive with dT | stage 4 |
| **Tectonics → CO2 source** | spreading and arc pulses are the CO2 term's main signal (±3 C) | source ×0.6–1.5 | keep: it's a fair forcing |
| **The random drift** (sd 3 C, 40 Myr) | passes almost whole into dT; makes the cold eras | dT/drift 0.82 | keep the drift; fix the brake (PW-368's narrowing reshuffled seeds only) |
| **Ice albedo** (tanh, 1.5 C per 3% of surface, level-off 3 C) | amplifies dT by ~1.2× | albedo term vs dT slope 0.05–0.29 | keep; the land-only albedo (A6) is fine short of snowballs |
| **Vegetation** | cooling greens the dry tropics (wrong sign, PW-454); no vegetation albedo term in the run's dT (PW-455) | PW-450: feedback ~0 on ice | low; leave to the vegetation lane |
| **4 Myr climate cadence, 5 Myr dT lag** | fine for the run's job; the per-update ice fixed point is the ice lane's issue | | keep |
| **Sea-ice switch × dT gap between run and zoom** | a small dT difference crosses the freeze of the nearest sea | 1.4 | stage 2 makes the switch geographic (where the cold air goes), not latitudinal |
| **Rain rule run (3%/C) vs zoom (7%/C)** | different snow for the same cooling | PW-563 | do it with stage 3 or with the ice lane's stage 3 |
| **The fixed latitude curve** | geography can't change a latitude's mean warmth: an Antarctica-like polar continent doesn't chill its hemisphere's ocean; no ocean-geometry effect on the pole-equator contrast | Southern Ocean +6 C annual; the overturning only redistributes in-band | later research (option E below) |

## 3. Measuring tools: what exists, what's missing

Exists and was used:
- `tools/earth_check.py`: Köppen, rain, temperature by band and region, rivers, clouds, moisture budget (~25 s at
  L6). **Bug:** the point table's "Kott" column and the region table's Kottek code read "Am" for nearly every place.
  The group shares above them are right (draft).
- **`tools/climate_bias.py` (new, this lane):** ice regions bare and iced; continentality by distance from the sea;
  west vs east coasts; summer heat by summer rain; a winter sea-ice proxy. `--dT` and `--set` (TUNE) for tests, ~15 s
  at L6. Sections 2–5 are mechanism checks that would run on a generated planet with no observations if the observed
  columns were dropped (stage 0).
- `tools/ice_diag.py`: the thermostat's terms per step. Enough to measure item 4's gain after the fact (section 1.5).
- `tools/tz_earth.py --dt0 / --greenland`: the Earth zoom's yardstick and the RACMO margin check (ice lane).
- `tools/ice_probe.py --stair`, `tools/ice_criteria.py`, `tools/sealevel.py`, `tools/health.py`, `tools/scorecard.py`
  (the latest line, 10-22, matches the earth_check numbers above; not re-run, since no model code changed).

Missing:
1. **An overturning report.** NH and SH sinking (Sv), each site's location and the basin's openness, the heat
   delivered (PW), and the inflow's path, on Earth and on generated planets. Today you have to print `moc_sites` by
   hand. The bisect above shows why it belongs in every climate change's check. (Stage 0, s.)
2. **The thermostat's gain, as a number** in `ice_diag --summary`: d ln(sink)/dT, the CO2 feedback in C per C, the
   dT/drift ratio, and the sink split into its land area, erosion supply, temperature factor and plant factor. (Stage
   0, s.)
3. **A planet-relative climate sanity check for generated worlds,** not Earth: sinking only in open seas; the sea-ice
   edge tilted by the winds (leeward seas freeze first); the seasonal range vs coast distance and land size; summer
   heat against summer cloud and rain. All as ranges, on 3–4 stored L6 worlds. (Stage 0, m.)
4. **Observed sea ice** for Earth (e.g. the NSIDC or HadISST monthly climatology) in `earth_data`, instead of the −5 C
   proxy. (s, needs a download.)
5. **An LGM check:** the model at dT ≈ −6 with the LGM ice (`earth_lgm_ice` exists) against gridded LGM temperature
   anomalies (Tierney et al. 2020) and the LGM sea-ice edge. This tests the *response*, which matters more for ice ages
   than today's state. (m, needs a download.)

## 4. Staged plan

Order: the cheap, high-leverage ocean fixes first, because they change the regional biases the most. Then summer heat,
then the thermostat, which is whole-run and needs 10-seed checks. Every stage re-runs earth_check, climate_bias, the
scorecard and the goldens. Every stage that changes the ice's climate also re-runs `tools/tz_earth.py` (both modes).
Stop rule per stage: 3 attempts, then report.

### Stage 0: tools (s; in this lane, can start now)
- climate_bias.py (done). The overturning report (missing 1). The thermostat gain in ice_diag (missing 2). Fix
  earth_check's Kottek column.
- Done when: the four print in one command each and a baseline table for main is recorded here.

### Stage 1: the overturning sinks in open polar seas (PW-458; m–l; climate/ocean lane)
- Physics: find which salinity term the rain kernel moved (rivers into the Arctic and Baffin, ice export, brine,
  leads) by factor separation on Earth's fixed geography, 1416523 against its parent. Then why the drift stops at
  55N.
- Not a fix: pinning sites, hosing, or moving `moc_lat`.
- **Done when (plausibility ranges):**
  - Earth's NH sinking is 8–20 Sv, ≥ 70% of it in seas open to the Atlantic north of 55N (Nordic, Irminger, Labrador),
    none in Baffin Bay.
  - The Norwegian coast's sea is ice-free in winter.
  - Fennoscandia's coldest month is within 6 C of the observed and its warmest within 3 C.
  - The SH sinking is unchanged or nearer the Weddell and Ross seas.
  - On 3 generated L6 worlds, no sinking in a basin smaller than `moc_sea_km2`.
  - The time zoom's Eurasian dT-0 caps (stage 1c: 0.72 Mkm2) at least halve.
- Effort ~1–2 agent-days. Risk: medium. The rain kernel is shared, and its moisture fixes (PW-015) mustn't be undone.

### Stage 2: the sea's air takes part in the carry; sea ice from the cold air (PW-346 broadened; m)
- Physics: a sea cell's winter air relaxes toward the air the wind brings it, at a rate set by how much open water there
  is. Open water warms the air (the water's heat), and a frozen sea is land-like ("a frozen sea moderates nothing").
  The freeze then follows the local winter air, not the latitude's.
- The summer side is PW-346's second bullet: ice-covered seas beside a continent get its outflow.
- **Done when:**
  - Hudson Bay, Okhotsk and Baffin Bay freeze in winter, with their coldest month within 8 C of the observed.
  - The Southern Ocean 60–70S winter is within 4 C.
  - The winter sea-ice proxy (or the observed set, missing 4) is within ±25% per hemisphere.
  - Labrador and the Hudson Bay lowlands winters are within 3 C.
  - The Arctic Ocean doesn't get worse (now ±1.3 C).
  - At dT −6 the southern sea ice stays within 1.5–2.5× today's.
- Effort ~1 agent-day. Risk: medium. It changes the sea-ice share that the overturning's brine reads, so do it after
  stage 1 and re-check stage 1's bars.

### Stage 3: summer heat from a surface energy split, and small lands (PW-352, PW-457, new draft; m–l)
- Physics:
  - The land's summer warming is the absorbed sun less what evaporation takes, so cloud cover and the summer's
    AET/PET set it, not a ±1.5 C table.
  - The land's "own" seasonal swing scales with how much land lies upwind within a continent's scale (~1000–2000 km),
    so narrow lands in a strong westerly are mostly the sea's air.
- Check it with the observed rain too: earth_check's `obs P` path does this for rivers. That separates the summer-heat
  error from the rain error.
- **Done when:**
  - Humid east coasts and interiors (SE USA, SE China, Great Lakes, Labrador, Hudson Bay lowlands) have a warmest month
    within 2.5 C of the observed, with dry interiors not more than 2 C colder than now.
  - The SH coastal seasonal range is within 1.3× the observed.
  - The NH continentality rows stay within 2 C.
  - Earth's zoom maxima don't get shallower than today's at the same cooling: a cooler Labrador should deepen them.
- Effort ~1.5–2 agent-days. Risk: medium-high. It touches every world's Köppen map and the rain (PW-015 stage 3 waits
  on it).

### Checkpoint: hand the zoom's honest rules their test (ice lane, s)
After stages 1–3, re-run with the zoom's new TZParams on:
- the L4 endings test (PW-568);
- `tz_earth.py` (maxima at ≤ 6 C, give-back ≥ 0.6, interglacial ice 9–12%);
- `--dt0` (within 20%, following the orbit);
- the moment suite.

If the L4 test still fails while the Earth bars move, that confirms it's the ice-surface air (PW-569/439), and it goes
back to the ice lane. I'd expect that.

### Stage 4: the thermostat, then the set point, then the star (PW-558, PW-559, PW-564, new draft; l; serial run lane)
1. The weathering law: a kinetic or supply limit, so erosion saturates and temperature and runoff steer. Then CO2 as a
   stock (PW-558 A, the ±6 e-fold range).
   - Done when the measured feedback is 0.4–0.9 C per C, the CO2 term is negative against dT on ≥ 70% of 10 seeds, and
     every deep era's CO2 term is warming.
2. The set point from the planet's own start balance (PW-559 B).
   - Done when the icehouse share is 15–45% on ≥ 7 of 10 L6 1 Gyr seeds, and the criteria's N1–N4 pass on ≥ 7.
3. Brightening (PW-564), planet-relative.
   - Done when the dT trend over 2 Gyr is ≤ ~3 C per Gyr and CO2 trends down.
- Effort ~2–3 agent-days plus ~2 × 10-seed L6 sweeps (~20 min each at 8 at once). Risk: medium. It changes every
  run's history, so the goldens and health must be refreshed.

### Later or optional
- **E. An energy-balance temperature curve.** A diffusive energy balance per latitude band with the planet's own
  albedo (ice, sea ice, clouds) and sunshine, in place of the fixed Earth curve.
  - It would make polar amplification, ice and sea-ice albedo, tilt, brightening and polar continents planet-relative
    in one go, and it's the honest route to snowball and waterbelt states.
  - It's a big change to everything downstream, and Earth's curve is a good fit today.
  - Lean: not in v2. Revisit if made-up planets with odd orbits (PW-481/443) need it.
- The coreless winter (1.3f): an annual mean that knows the shape of the polar year. Small; fold into PW-039.
- Winter maritime air inland (PW-026) and moisture to high latitudes (PW-015): those lanes' own tickets. Stages 1–2
  will change their numbers, so re-measure before working them.

### Where "close enough" is
Stop when all of these hold, and don't chase further:
- On the ice regions table, summers are within ±3 C and winters within ±6 C on ≥ 80% of rows.
- Earth's sinking is in open polar seas at 8–20 Sv.
- The southern sea ice is within ±25%.
- The thermostat's feedback is 0.4–0.9 C per C.
- The icehouse share is 15–45% on ~70% of seeds.

Earth's remaining particulars (the Gulf Stream's separation, Tibet's rain, the Sahara's dryness) don't change whether a
made-up world is plausible, and they aren't worth deeper simulation.

## 5. Judgement calls (inbox drafts on this branch)
- `draft-base-climate-plan-order.md` (needs-decision): the stage order and scope above. It includes keeping the
  margins' ice-surface air in the ice lane, and fixing the thermostat before choosing the set point and adding the star.
- `draft-overturning-flipped-by-rain-kernel.md`: the bisect for PW-458 (merge into it).
- `draft-sea-air-only-knows-its-water.md`: PW-346 broadened to every leeward and enclosed sea (merge into it).
- `draft-weathering-sink-barely-answers-temperature.md` (needs-decision): the measured gain and the law's options.
- `draft-small-lands-big-continent-seasons.md`: the SH seasonal range.
- `draft-annual-mean-coreless-winter.md`: for PW-039 (merge into it).
- `draft-earth-check-kottek-column.md`: the tool bug.
- `draft-overturning-and-thermostat-reports.md`: the two missing tools (stage 0).
