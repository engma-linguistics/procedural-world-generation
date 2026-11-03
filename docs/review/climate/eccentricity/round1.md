# PW-1365 round 1: worlds across orbital eccentricity (lane 148, 2026-11-03)

Investigation only: nothing under `planet/` changes. Code at main 8f4976fa.

## 1. Diagnosis (written before the screen)

### Where eccentricity enters the code

| Place | What it does with e | Code |
|---|---|---|
| The run's climate (1 Gyr `simulate`) | **Nothing.** `climate.compute` builds its seasons from the tilt only (`season_strength(grid, tilt)`), i.e. a circular orbit. The run's global temperature has no `(1-e^2)^-1/2` term either. | `planet/climate.py::compute`, `planet/tectonics/earth.py` |
| The run's ice (the ice-age cycle mean) | A fixed `ECC = 0.03` ("the rms of the time zoom's"): the ice balance is averaged over 4 perihelion phases x 2 obliquities at that e, each month's insolation change x `INSOL_K` 0.25 C per W/m2 (0.3 of that at sea). | `planet/icemass.py::cycle_dq`, `OBL_AMP, ECC` |
| The time zoom's orbit | `ecc_mean 0.027 + ecc_100 0.015 cos(100 kyr) + ecc_400 0.010 cos(405 kyr)`, clipped at 0; phases drawn from the seed (`phases='seed'`). So every planet's e lies in **0.002-0.052**, mean 0.027. Settable with `--set ecc_mean=...`. | `planet/timezoom/params.py::TZParams`, `planet/orbit.py::orbit_at` |
| The time zoom's ice rule | Each month's insolation change against the mean orbit (`orbit_ref='mean'`: the tilt, e = 0) x the 'run' rule (0.25 C per W/m2 on land), so the zoom's ice sees the orbit at ~3x the land's seasonal response. | `planet/timezoom/forcing.py::orbit_anomaly`, `own_k` |
| The finished world (PW-1325) | `finish.orbit_dt` adds the frame's orbit (obliquity, e, perihelion) as a monthly anomaly against the mean orbit, at each cell's **own seasonal response** (`icemass.seasonal_k`: its swing per the sun's swing, ~0.08-0.09 C per W/m2 on mid/high-latitude land, ~0.02 at sea). `climate._orbit` adds the anomaly's **July and January** months to the warm/cold half-years and its 12-month mean to the annual mean. The anomaly includes the orbit's annual-mean gain. The carbon cycle does not answer it (a frame is a moment). | `planet/finish.py::orbit_dt`, `planet/climate.py::_orbit` |
| `planet make` | Lists "orbit (distance, eccentricity)" as UNSUPPORTED: there is no world-builder knob for the run. | `planet/make.py::UNSUPPORTED` |

So today the generator never draws an eccentricity from a range: it hard-codes Earth's cycle (0.002-0.052) in the
time zoom and 0.03 in the run's ice. The run, which sets every hard-bar outcome (frozen over, hell, ocean loss, CO2
crash), never sees the orbit's annual-mean gain or its seasons.

Two structural limits matter as e grows:
1. **Two-point seasons.** The climate keeps only a warm and a cold half-year (July and January of the anomaly).
   With e > ~0.2 the near-sun passage is short (Kepler) and does not stay on the solstice. At perihelion on the
   northern solstice (peri = 90 deg), the monthly anomaly's largest month is 292 W/m2 at e = 0.2 and 686 W/m2 at
   e = 0.4. July, the month the model reads, gets 199 W/m2 (20 N) and 161 W/m2 respectively (`orbit.insolation`,
   computed here). So above ~0.2 the model **under-reads** the hot season. And when perihelion is near an equinox
   it reads almost none of it: only the annual mean gets through.
2. **Linear response.** The response is a C-per-W/m2 slope fitted to the planet's own seasons. That is fine for
   tens of W/m2. At e = 0.2-0.3 the perihelion month brings +200-450 W/m2, beyond anything the slope was fitted on.

### What physics says (sources read this session; full text unless marked)

- **Earth's range.** "Currently, the Earth's eccentricity oscillates between almost zero and about 0.06 with a
  ~100,000 year periodicity" (Spiegel, Menou & Scharf 2010, ApJ 721, 1308; arXiv:1002.4877, Sec. 1, p. 2).
  Laskar et al. 2011 (La2010, A&A 532, A89; arXiv:1103.1084, Sec. 7, p. 9 of the arXiv PDF) give eccentricity terms of about
  95 and 124 kyr. The 405 kyr term (g2 - g5) is "the largest term in a quasi periodic approximation of the
  eccentricity of the Earth". Fig. 3 (p. 7) plots the solutions 30-50 Myr ago, all within 0-0.06. (Berger & Loutre 1991 and Laskar et
  al. 2004 could not be read: paywall / 403. Their numbers are not used.)
- **Annual mean.** Annual-mean irradiation grows "in proportion to (1 - e^2)^-1/2" (Spiegel et al. 2010, Sec. 1,
  p. 2; Dressing et al. 2010, ApJ 721, 1295, Sec. 2, ar5iv HTML via a summarising fetch). Gains: +0.05% at 0.03,
  +0.18% at 0.06, +0.5% at 0.1, +2.1% at 0.2, +4.8% at 0.3, +9.1% at 0.4 (computed). At the run's own sensitivity
  (238 W/m2 per unit luminosity x 0.81 C per W/m2; `tectonics/earth.py::star_forcing`) that is +0.09, +0.35,
  +0.97, +3.97, +9.3 and +17.5 C before the carbon cycle answers. La2010 Sec. 7.2 (p. 12) also notes the global
  mean "varies as e^2 and thus is not much influenced by eccentricity variations, this is not the case for seasonal
  variations".
- **Seasonal swing.** The perihelion/aphelion flux ratio is ((1+e)/(1-e))^2 (Dressing et al. 2010, Sec. 2):
  1.13 at 0.03, 1.27 at 0.06, 1.49 at 0.1, 2.25 at 0.2, 3.45 at 0.3. La2010 Eq. (1), Sec. 7.2, p. 12: for a bare black
  body dT/T ~ e, so "a change of 0.02 in the eccentricity corresponds ... to a change of about 0.02 x 300 = 6 K"
  between perihelion and aphelion. That is an upper bound: oceans damp it.
- **Habitability vs e.** Williams & Pollard 2002 (Int. J. Astrobiol. 1, 61; **abstract only**): long-term climate
  stability depends on "the average stellar flux received over an entire orbit, not the length of the time spent
  within the HZ". Way & Georgakarakos 2017 (arXiv:1611.06133, Sec. 1, full text) summarise them: e of 0.1-0.7 at
  1 AU stays below the moist-greenhouse and runaway limits "as long as eccentricities are less than 0.42 and 0.70".
  Way & Georgakarakos's own coupled-ocean GCM, with e varying 0-0.283, "maintain[s] relatively temperate
  climates". Its hottest grid point at peak e was 53.9 C (Sec. 3, Fig. 4A), "very far from approaching a
  moist-greenhouse state". Dressing et al. 2010 (EBM, 50 m mixed layer, ocean heat capacity 40x land; Table 1):
  "the habitability of planets with e >~ 0.30 depends on the season" (Sec. 5.1, Fig. 7). Their outer habitable
  edge moves out roughly as (1-e^2)^-1/4 up to e ~ 0.65 (Fig. 9). At least 10% ocean buffers against freezing at
  apoastron (abstract). Spiegel et al. 2010: without a CO2 thermostat a high-e planet can pass 400 K (Sec. 5).
  With one, a 1 AU planet at e = 0.8 settles (Fig. 1, via summary). Bolmont et al. 2016 (A&A 591, A106,
  **abstract only**): the mean-flux approximation fails at high e.
- **Real planets.** Kipping 2013 (MNRAS 434, L51, **abstract only**): RV planets fit Beta(a = 0.867, b = 3.03).
  Van Eylen et al. 2019 (AJ, arXiv:1807.00549, **abstract only**): single-transit small planets fit a half-Gaussian
  with sigma 0.32. Multi-planet systems are near circular.

(Part of the Dressing and Spiegel reading came through a summarising fetch. Section/figure pointers are given where
page numbers were not available; the Spiegel Sec. 1 and Way & Georgakarakos quotes were read verbatim.)

### Predictions (before the screen)

Run screen: the run's ice cycle gets ECC = e, and the annual-mean gain goes in as `climate_offset` at the run's
sensitivity (so the weathering thermostat answers it).
1. e <= 0.06: no hard-bar change. The run's annual term is <= 0.35 C, inside roll noise. Land ice changes a little:
   a larger ECC means stronger perihelion summers in the cycle mean, so somewhat **less** land ice.
2. e = 0.1: about +1 C before the carbon cycle; CO2 lower by ~20%; no new hard failures.
3. e = 0.2: about +4 C. The thermostat answers by cutting pCO2 by ~2^(4/3) ~ 2.5x (to ~110 ppm from ~280). That
   is near the plants' compensation point: **the CO2 crash bar is the first to go**, before hell.
4. e = 0.3-0.4: +9 to +17.5 C. pCO2 would have to fall 8-60x: CO2 crash on every seed. At 0.4 hell is likely too
   (the median dT bar is +10.5 C).
5. Frozen-over gets rarer as e grows: more annual sun and a hotter perihelion summer in the ice cycle.

Finished-world screen (an unchanged run, a 100 kyr time zoom at a fixed e, finished at perihelion on the northern
summer solstice):
6. The perihelion hemisphere's July land warms by the seasonal slope x the July anomaly: about +2-3 C at 0.03, +5 C
   at 0.06, +8 C at 0.1, ~+15 C at 0.2 at 20-45 N. The other hemisphere's January is about as much colder. Land
   >= 35 C (today ~3% on dba204 after PW-1325) climbs steeply past 0.06. Above ~0.2 the model under-reads (limit 1).
7. The zoom's ice, under the 'run' rule at 3x the seasons' slope, swings much harder than the finish's climate. It
   probably melts out in the perihelion hemisphere and grows in the other.

## 2. Screen

Scratch only (`PLANET_DATA` = lane 148's scratch dir, deleted afterwards). L6, main 8f4976fa.

### 2a. Finished worlds: the seasons (unchanged runs, the orbit only in the time zoom and the finish)

Two runs: seed 957317 (run bd9eaa, finished at 1000 Myr, a 14.4 C world) and seed 619496 (run 67d697, 991 Myr, a
warm 19.2 C world). From each, a 100 kyr time zoom with a **fixed** e (`--set ecc_mean=E ecc_100=0 ecc_400=0`)
was finished at its end. Phases were set so perihelion falls on the **northern summer solstice** at the end
(`phases=0,324.8,0,0`, perihelion 90 deg), the worst case for one hemisphere. Measured with `measure.py`. All
shares are area-weighted. "Hot" and "no thaw" are shares of ice-free land; ice is the share of all land.
Baseline: **the same seed at e = 0.017** (Earth today); e = 0 is the circular orbit.

Seed 957317 (14.4 C):

| e | land >= 35 C (warmest month) | N / S hemisphere | land >= 30 C | no thaw (warmest < 0 C) | land ice | mean warmest / coldest month (open land) | tundra / boreal | hot desert |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.0% | 0.0 / 0.0 | 3.7% | 0.1% | 9.6% | 22.3 / 7.3 C | 2.7 / 5.8% | 4.3% |
| **0.017** | **0.1%** | 0.1 / 0.0 | **3.9%** | **0.1%** | **9.9%** | **22.5 / 7.6 C** | **2.1 / 5.8%** | **3.9%** |
| 0.03 | 0.2% | 0.4 / 0.0 | 4.5% | 0.1% | 9.3% | 22.5 / 7.5 C | 2.5 / 5.9% | 3.7% |
| 0.06 | 1.8% | 3.5 / 0.0 | 9.2% | 0.4% | 8.8% | 22.5 / 7.4 C | 3.4 / 6.2% | 3.4% |
| 0.1 | 4.5% | 8.8 / 0.0 | 16.5% | 1.5% | 7.1% | 22.5 / 7.1 C | 4.6 / 6.2% | 3.4% |
| 0.2 | 18.1% | 35.5 / 0.0 | 29.9% | 3.4% | 5.2% | 24.1 / 6.7 C | 8.0 / 3.1% | 2.8% |
| 0.3 | 23.5% | 42.0 / 4.3 | 41.0% | 4.4% | 4.9% | 25.8 / 6.2 C | 8.1 / 2.0% | 3.0% |
| 0.4 | 15.8% | 18.4 / 13.1 | 36.1% | 4.8% | 4.5% | 24.3 / 5.0 C | 6.5 / 2.4% | 3.2% |

Seed 619496 (19.2 C, a warm world):

| e | land >= 35 C | N / S | land >= 30 C | no thaw | land ice | warmest / coldest | tundra / boreal | hot desert |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.5% | 0.9 / 2.0 | 22.7% | 0.1% | 3.2% | 25.2 / 6.9 C | 1.7 / 6.3% | 4.6% |
| **0.017** | **2.6%** | 4.2 / 1.0 | **23.0%** | **0.2%** | **3.2%** | **25.4 / 7.1 C** | **1.7 / 5.7%** | **4.7%** |
| 0.03 | 3.7% | 7.3 / 0.1 | 22.3% | 0.5% | 2.4% | 25.3 / 6.8 C | 2.3 / 5.6% | 4.8% |
| 0.06 | 7.1% | 14.2 / 0.0 | 21.0% | 0.2% | 2.2% | 25.4 / 6.9 C | 2.9 / 5.5% | 5.1% |
| 0.1 | 12.0% | 24.0 / 0.0 | 26.5% | 0.2% | 2.0% | 25.9 / 7.1 C | 3.6 / 5.4% | 4.9% |
| 0.2 | 26.0% | 51.1 / 1.1 | 41.7% | 1.9% | 1.7% | 27.9 / 7.3 C | 3.8 / 5.6% | 5.2% |
| 0.3 | 30.4% | 50.8 / 10.1 | 52.9% | 2.9% | 1.7% | 29.1 / 6.8 C | 3.9 / 4.2% | 4.4% |
| 0.4 | 24.1% | 24.9 / 23.4 | 44.5% | 3.5% | 1.5% | 26.5 / 5.9 C | 4.8 / 4.7% | 4.2% |

The same seed 957317 with perihelion on the **March equinox** (`phases=0,234.8,0,0`) instead, against its own
e = 0 (land >= 35 C / >= 30 C / no thaw / land ice / warmest and coldest month):
e = 0: 0.0 / 3.7 / 0.1 / 9.6% / 22.3, 7.3 C. e = 0.03: 0.0 / 3.4 / 0.2 / 10.8% / 22.3, 7.6 C.
e = 0.1: 0.0 / 2.3 / 2.0 / 6.1% / 21.0, 6.4 C. e = 0.2: 0.0 / 0.2 / 4.6 / 2.1% / 18.7, 4.9 C.
e = 0.3: 0.0 / 0.0 / 8.5 / 0.7% / 15.9, 4.0 C.

What this shows:
- **Earth's range is safe and already in.** Up to e = 0.03 the hottest-hemisphere land >= 35 C rises by at most
  a few points over the same seed at 0.017 (957317: 0.1 -> 0.2%; 619496: 2.6 -> 3.7%). Nothing else moves beyond
  noise. At 0.06 (the top of Earth's own range) the share is 1.8% on the temperate world and 7.1% on the warm one.
  That is a markedly hotter perihelion-hemisphere summer, but still a plausible one.
- **0.1 is where it starts to read as a different planet.** On the warm world 24% of northern ice-free land has a
  warmest month >= 35 C (same seed at 0.017: 4.2%), and there is 8.8% on the temperate one (0.1%). The southern
  summer at aphelion grows colder: land with no thaw month goes 0.1 -> 1.5% (957317).
- **At 0.2-0.3, half of the perihelion hemisphere's land is >= 35 C in its warmest month** (619496: 51%). The
  other hemisphere's summers barely thaw (957317: 3-4% of land with no month above 0 C). Tundra roughly triples
  (957317: 2.1 -> 8.0%).
- **Above ~0.2 the model breaks, as diagnosed (limit 1).** At 0.4 the hot share falls back (957317: 23.5 ->
  15.8%) because the model reads July and January, and the near-sun spike no longer lands in July. With
  perihelion at an equinox it reads none of the spike: at e = 0.3 the world gets *colder* in both seasons (warmest
  month 22.3 -> 15.9 C), although its annual sunlight is 4.8% higher. Meanwhile its ice melts (9.6 -> 0.7%),
  because the time zoom's ice sees all 12 months. So above ~0.1 the model's seasons depend on where perihelion
  falls in the calendar, which is an artefact. Its numbers there are not trustworthy in either direction.
- **Biomes barely respond.** Hot desert, rainforest and savanna shares stay within ~2 points up to 0.4. Only
  tundra (up) and boreal forest (down) move. The biome rules key mostly on annual temperature and rain, so a
  45 C perihelion summer does not show as a biome. The heat shows in the warmest-month layer only (and in
  whatever peoples and crops read from it).
- **The time zoom's ice shrinks steadily with e** (957317: 9.9% at 0.017 -> 7.1% at 0.1 -> 4.5% at 0.4). Under
  the zoom's 'run' rule (3x the seasons' slope), the strong perihelion summer melts more than the cold aphelion
  summer saves. That is prediction 7, minus the regrowth in the other hemisphere, which did not happen.

### 2b. Runs: the hard bars, ice ages and CO2 (1 Gyr, L6)

Four seeds from the paired judge's draws (`docs/review/base-climate/v1-finish-16/paired.sh`: 957317, 619496,
583167, 639472), roll 0.0005, `star_brightening=1.0`, through `tools/ice_diag.py`. They ran from a scratch copy
of the code with two env-var knobs (scratch only, never committed): `icemass.ECC` (the run's ice-cycle e) and,
for the "s" arms, a luminosity factor `(1-e^2)^-1/2` on `tectonics/earth.py::star_forcing`, which the carbon
cycle answers. The plain arms put the yearly gain in `climate_offset` instead. I meant that as the same forcing,
but the weathering's reference is learnt at the balance climate *plus* `climate_offset` (`earth.py`, the
`REF_FREEZE` block), so the thermostat **keeps** that shift rather than answering it. The plain arms are
therefore "no carbon-cycle answer" upper bounds; the s arms are the physical reading.
**Baseline: the same four seeds on today's code ("today", the run's ice at e = 0.03).** After 300 Myr: medians and
ranges over the 4 seeds. Per-draw rows: `runs_results.txt`. Hard bars: `tools/hard_bar.py`.

| arm (run's ice e; yearly gain) | soft pass | hard: frozen / hell / ocean / CO2 crash | dT median (C, range of seeds) | pCO2 median / min (ppm, ranges) | land under ice, median (%) | time in icehouse (%) |
|---|---|---|---|---|---|---|
| **today (0.03; none)** | **3/4** | **0 / 0 / 0 / 0** | **+0.0 .. +6.5** | **848-3402 / 119-350** | **1.4-8.1** | **21-68** |
| e = 0.06 (0.06; offset +0.35 C) | 4/4 | 0 / 0 / 0 / 0 | +0.7 .. +4.3 | 870-2578 / 113-331 | 1.4-4.5 | 9-51 |
| e = 0.1 (0.1; offset +0.97 C) | 1/4 | 0 / 0 / 0 / 0 | +2.9 .. +5.4 | 950-2718 / 118-268 | 0.0 | 0-1 |
| ablation: ice e 0.1, no gain (2 seeds) | 1/2 | 0 / 0 / 0 / 0 | +1.7 .. +4.6 | 1249-2226 / 115-514 | 0.0-0.6 | 0-1 |
| e = 0.2, offset (+3.97 C kept) | 0/4 | 0 / 0 / 0 / 0 | +5.2 .. +9.1 | 666-2494 / 120-260 | 0.0 | 0 |
| **e = 0.2, star (answered)** | 0/4 | 0 / 0 / 0 / 0 | +2.7 .. +6.5 | 500-1082 / 102-170 | 0.0 | 0 |
| e = 0.3, offset (+9.3 C kept) | 0/4 | 0 / **4** / 0 / 0 | +11.6 .. +14.1 | 826-2286 / 111-195 | 0.0 | 0 |
| **e = 0.3, star (answered)** | 0/4 | 0 / 0 / 0 / 0 | +6.3 .. +9.3 | 319-652 / 84-113 (3/4 < 100) | 0.0 | 0 |
| e = 0.4, offset (+17.5 C kept) | 0/4 | 0 / **4** / 0 / 0 | +19.4 .. +23.4 | 747-1592 / 99-196 | 0.0 | 0 |
| **e = 0.4, star (answered)** | 0/4 | 0 / **4** / 0 / **3** | +10.7 .. +13.7 | 107-218 / 34-82 | 0.0 | 0 |

(e = 0 was dropped for the s arms; nothing in the e = 0.06 row suggests e = 0 differs from today beyond its ice.)

What this shows:
- **The run's ice ages are the first thing to go, at e ~0.1, and that comes from the model's rule, not
  physics.** The ablation keeps only the ice-cycle e (0.1) and no yearly gain. Land ice still vanishes on both
  seeds (icehouse time 0-1%, against 57-68% for the same seeds today). The cause is the ice cycle's 0.25 C per
  W/m2 (`INSOL_K`, ~3x the land's seasonal response, PW-459). With it, a perihelion summer at e = 0.1 (+~100 W/m2)
  melts as if +25 C. Earth at e 0.04-0.06 had its ice ages, so a real planet at 0.1 would plausibly keep some.
  Already at 0.06 the icehouse time falls (957317: 68 -> 12%).
- **Soft passes fall from 3/4 to 1/4 at 0.1 and to 0/4 from 0.2.** The finish moment's temperature check fails:
  with no ice, the worlds end +4 to +8 C warm. No hard bar fires up to 0.3 when the carbon cycle answers the
  yearly gain.
- **Hard bars: the hellhouse is the first, at 0.4** (4/4, dT median +10.7 to +13.7 C), with the CO2 crash on 3/4
  (pCO2 34-56 ppm, below the plants' compensation point). At 0.3 the thermostat holds the climate (+6 to +9 C)
  but strains: 3 of 4 seeds dip below 100 ppm. Viable turns unviable between **0.3 and 0.4** on the hard bars,
  and at **~0.1** on the soft scorecard, because of the run's ice rule.
- No frozen-over and no ocean loss at any e: eccentricity only adds sunlight.

### 3. Predictions scored

1. Right on the hard bars (none at <= 0.06). Wrong on the ice: "a little less" was a large drop at 0.06 in
   icehouse time (68 -> 12% on one seed; 21-68% -> 9-51% over all four).
2. Wrong: at 0.1 the run's ice ages disappear. I under-estimated the 3x run rule.
3. Wrong: at 0.2 no CO2 crash (min 102-170 ppm). The thermostat cut the median pCO2 by roughly half to two-thirds (500-1082 against 848-3402 ppm), not to ~110 ppm, and let the
   world warm +3-6 C instead.
4. Half right: at 0.4, hell 4/4 and CO2 crash 3/4. At 0.3 the thermostat held (no hard bar).
5. Right: no frozen-over anywhere.
6. Right in shape, and the ">= 35 C climbs steeply past 0.06" held. The under-read above 0.2 came out as
   predicted, and worse when perihelion is off the solstice (2a).
7. Half right: the zoom's ice shrinks. The other hemisphere did not regrow it.

## 4. Conclusions

- **Earth's own range, 0-0.06, is safe on every measure.** It is also what the time zoom already draws
  (0.002-0.052). The finished worlds' perihelion-hemisphere summers get hotter at 0.06 (land >= 35 C: 1.8-7.1%,
  against 0.1-2.6% for the same seeds at 0.017), but stay plausible. The runs pass and lose some ice-age time.
- **0.06-0.1 is the edge of what the model handles soundly today.** The run's ice ages vanish at 0.1 (rule
  overshoot), and summers of 35 C+ cover a quarter of the hot hemisphere's land on a warm world.
- **0.1-0.3 is physically habitable** (Way & Georgakarakos 2017: a coupled-ocean GCM at e up to 0.283 stays
  temperate; Dressing et al. 2010: season-dependent habitability from ~0.3). It is not modelled soundly here:
  two-point seasons, a run that ignores the orbit, and an ice rule at 3x the seasonal response. These are
  "strong-season worlds" for the weird-worlds work (PW-443).
- **Above ~0.35-0.4 the planet boils on the hard bar even with the carbon cycle answering.**
- The biomes barely register the seasons. Heat extremes live in the warmest-month layer only.

Recommendation and options: `issue-tracking/inbox/draft-eccentricity-range-for-earthlikes.md`. Follow-ups:
`draft-run-ignores-orbit-eccentricity.md`, `draft-eccentric-orbit-two-point-seasons.md`.

Files: `measure.py` (world measures), `runs_summary.py` (run measures), `runs_results.txt`,
`worlds_results.jsonl`. The scratch runs and worlds are deleted; the world ids in the tables are gone.
