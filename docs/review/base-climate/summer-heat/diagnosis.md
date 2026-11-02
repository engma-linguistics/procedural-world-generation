# Lane 121: summer heat (PW-1279, PW-1322 draft). Diagnosis and cheap screens, 2026-11-02

Status: **diagnosis and screens only; nothing merged into the model.** Main ff5fb965. The candidate code is parked
as [candidates.patch](candidates.patch). Both knobs are off by default, so with them off the model is unchanged.

## In plain words

- **Most of dba204's hot tropical July isn't the climate model.** A finished world adds the time zoom's orbit to
  every month. It turns the change in sunshine into degrees with the ice rule's 0.25 C per W/m2, which PW-459 already
  found is ~3x the land's seasonal response. dba204's frame has eccentricity 0.035, with the near-sun point in
  northern summer. That's +32 W/m2 in July at the equator, so **+8 C on tropical land.**
  - Re-solving dba204's climate without the orbit gives a warmest month of 25.2 C at 0-20 deg, not 30.5.
  - With the orbit at the seasonal response (PW-459's option a), it's 25.2 too, and land with a warmest month
    >= 30 C falls from 45% to 19%.
  - A one-line decision for finish.py; see the draft and Recommendation 1.
- **On Earth itself, the model's tropics aren't too hot. They're 1.9 C too cool in summer.** The excess is in the
  subtropics, 20-40 deg: +2.1 C, and 7.9% of land reaches a warmest month of 35 C against 1.7%. The worst spots
  are the Sahara (+4.7), the dry humid coasts (SE USA +5.1, Pampas +6.4, E Australia +4.9), SE China (+2.6) and
  N Mexico (+2.6).
- **All of that excess is the summer energy split** (`planet/climate.py::_summer_split`). With the split off,
  20-40 deg is 1.1 C *cool*, and no land reaches 35 C. The split heats sunny dry land by the sunshine it gets less
  what it evaporates. It does this:
  - with no extra long-wave loss under clear skies;
  - into a boundary layer fixed at 1500 m, while a desert's real one is 4-6 km deep.
- **The rain deficit (PW-1322's question) is a small part.** The observed rain removes ~10% of the 20-40 deg excess,
  and a fifth to a quarter on the dry humid coasts (SE USA 5.1 -> 4.0 C). The observed evaporation (NCEP) removes
  ~a third: Budyko on the right rain still evaporates half of what those coasts do.
- **Two sourced candidates both move it the right way.**
  - A boundary layer that deepens with the ground's heat (Ryder et al. 2015: the Saharan one reaches 5-6 km): 20-40
    deg +2.1 -> +0.7, and >= 35 C land 7.9% -> 1.5% (obs 1.7%).
  - Plus FAO-56's clear-sky long-wave loss: +0.4 and 0.7%.
  - Köppen and rain hardly move (B 25.0 -> 24.6, against Kottek's 30.1).
  - They don't fix the humid coasts. Those need the rain (PW-015's supply round).

## 1. How the summer temperature is built now

- `planet/climate.py::_air_temps` builds the land's summer air in three steps:
  - The land is left to itself: the latitude curve plus `continental` x season strength.
  - `planet/climate.py::_summer_fetch` mixes it with the arriving sea air.
  - Then it is carried along the summer wind (`carry`, reach U x `sum_tau`).
- `planet/climate.py::compute` adds `d_sum`, the **summer energy split** (`planet/climate.py::_summer_split`), after
  the rain:
  - d_sum = sum_tau / (rho c sum_h) x [(SW - LE) - (SW_ref - LE_ref)], where 86400 s / (1206 x 1500 m) = **0.048 C
    per W/m2**.
  - SW = (1 - 0.21) x the summer sun at the ground x (0.25 + 0.5 sunshine(cloud)).
  - LE = the Budyko summer evaporation.
  - The reference stands for the curve's typical surface: cloud_ref 0.63, so sunshine 0.38, and LE_ref = 0.61 x PET.
  - There is no long-wave term, and the depth is fixed.
- `planet/climate.py::_land_finish` adds the vegetation's albedo (+-2 C cap).
- A finished world adds `orbit_dt` (`planet/finish.py::orbit_dt` -> `planet/timezoom/forcing.py::orbit_anomaly`,
  via `planet/climate.py::_orbit`).

## 2. dba204: the orbit, then geography

`world_bands.py` (this folder) reads the stored world and re-solves its climate (`vegetation.coupled_climate` on its
elevation and ice at dT 0.7). With `--orbit 22.426,0.0348,90.7 0.7` it adds the finished frame's orbit anomaly
(time zoom 56dee1: orbit_resp 'run', orbit_ref 'mean') under the 'run' and the 'seasons' responses.

| dba204, ice-free land | stored | re-solved + orbit 'run' | + orbit 'seasons' | no orbit | split off, no orbit |
|---|---|---|---|---|---|
| warmest month 0-20 deg (annual) | 30.5 (23.1) | 30.5 (23.1) | 25.2 (22.7) | 25.2 (22.7) | 27.1 (23.7) |
| 20-40 deg | 28.7 | 28.6 | 28.2 | 28.0 | 25.3 |
| 40-60 deg | 22.6 | 22.7 | 19.8 | 18.6 | 20.1 |
| land >= 30 C | 45.4% | 45.4% | 19.0% | 18.4% | 11.9% |
| land >= 35 C | 18.3% | 18.1% | 6.3% | 5.4% | 0% |

- The 'run' re-solve reproduces the stored world. So **~5.3 C of the 0-20 deg warmest month, and 26 of the 45 points
  of land >= 30 C, are the orbit at 0.25 C per W/m2.**
- The insolation change for this orbit against a circular orbit is +31-32 W/m2 in July at 5-25 N and 5-15 S, and
  -16 to -36 in January (orbit.insolation, each month averaged with the one before). At 0.25 that is +7.7-8.0 C on
  land, shrunk near coasts by the 600 km mixing with the sea's 0.3x.
- With the climate's own seasonal response (`planet/icemass.py::seasonal_k`: the cell's swing per the sun's
  range, ~0.03 at 0-20 deg) it adds ~1 C in July.
- **Source for the size of the response.** Braconnot et al. 2007 (PMIP2 part 1, Clim. Past 3:261), mid-Holocene:
  "an increase by 26 W/m2 of the seasonal cycle of the incoming solar radiation ... in the northern hemisphere".
  The continental summer warming "reaches a maximum of about 2 C in central Eurasia and over the Tibetan Plateau".
  "The region extending from West Africa to the north of India is colder than today", because of the stronger
  monsoon's cloud and recycling. So on land it's <= ~0.08 C per W/m2, and negative in the monsoon tropics. The
  'seasons' rule fits that, and 0.25 doesn't.
- **Geography.** dba204 has 40% of its ice-free land at 0-20 deg; Earth has about 31% (my band areas). Without the
  orbit its 0-20 deg warmest month (25.2) is close to Earth's model (24.6). Its >= 30 C share (18.4%) is close to
  Earth's model (17.8%) and NCEP (16.1%), and its >= 35 C share (5.4%) is close to Earth's model (7.9%). So beyond
  the orbit, dba204 shows the same base-climate tail as Earth: section 3.

## 3. Earth L7: the base climate's warm month, split by cause

`diag.py` (this folder) runs `vegetation.coupled_climate` on Earth L7, as earth_check does, with swaps inside the
summer split. Land is ice-free, north of 60 S, against NCEP 2 m (data/earth L7 obs_t_warm, read from a private
copy). The swaps:
- **rain**: GPCC land rain into `climate.water_balance`, so the split's evaporation is the observed rain's. The rain
  kernel and the clouds keep the model's rain.
- **le**: NCEP's summer-half latent heat in place of the split's LE.
- **sun**: CRU's summer sunshine share in place of sunshine(cloud).
- **nosplit**: d_sum = 0.

### By latitude band (warmest month, model (bias vs NCEP); d_sum = the split's mean warming)

| band | NCEP | main | rain swap | LE swap | sun swap | LE+sun | split off | main d_sum (sun part, LE part) |
|---|---|---|---|---|---|---|---|---|
| 0-10 | 24.9 | 23.5 (-1.5) | -1.1 | -1.4 | +0.3 | +0.2 | +1.1 | -3.8 (-2.1, -1.7) |
| 10-20 | 28.0 | 25.7 (-2.3) | -1.5 | -1.8 | +0.1 | +0.6 | -1.0 | -1.8 (-1.4, -0.4) |
| 20-30 | 27.9 | 30.4 (+2.5) | +2.3 | +2.0 | +3.0 | +2.5 | -0.9 | +3.6 (+1.7, +1.9) |
| 30-40 | 22.8 | 24.4 (+1.6) | +1.3 | +0.6 | +1.8 | +0.8 | -1.4 | +3.5 (+2.2, +1.3) |
| **20-40** | 25.6 | 27.7 (**+2.1**) | **+1.9** | **+1.4** | +2.4 | +1.7 | **-1.1** | +3.6 (+1.9, +1.7) |
| 40-60 | 18.5 | 18.3 (-0.2) | +0.3 | -0.8 | +1.5 | +0.9 | +0.8 | -1.0 (-0.5, -0.5) |
| land >= 30 C (NCEP 16.1%) | | 17.8% | 18.7 | 17.6 | 22.5 | 21.8 | 10.2 | |
| land >= 35 C (NCEP 1.7%) | | 7.9% | 7.2 | 7.3 | 8.1 | 8.5 | 0.0 | |

The annual-mean biases are small: 20-40 deg -0.2, 0-20 deg -1.5, 40-60 deg +0.7. **So this is a summer-swing
problem, not an annual one.** By cause:

- **Soil moisture and evaporative cooling (the rain deficit).** The rain swap is ~10% at 20-40 deg. The band's summer
  rain is close to GPCC's (704 vs 759 mm/yr), because it's dominated by deserts. The LE swap is ~33% there: the
  model evaporates 38 W/m2 against NCEP's 53. Regionally it's larger on the dry humid coasts (next table).
- **Cloud and sunshine.** At 20-40 deg the model's summer sunshine is 0.61 against CRU's 0.67, so the cloud isn't
  what's heating it. The split's sun term is +1.9 C there because the reference is on the sky-cover scale (0.38),
  not because the model is too sunny.
  - In the wet tropics the split's sunshine is 0.12-0.22 against CRU's 0.46-0.57. It reads the sky's total cover,
    without the convective discount the plants use (`shade`). That cools 0-20 deg by ~2 C. The sun swap removes the
    whole 0-20 deg cool bias.
  - That's a separate bug, the opposite way: [draft-summer-split-overcast-tropics](../../../../issue-tracking/inbox/draft-summer-split-overcast-tropics.md).
- **Land heat capacity and the seasonal amplitude.** Not the cause. With the split off, the base swing (continental
  24 x season strength, fetch-mixed) gives 20-40 deg -1.1, and the coldest month is 1.7 C too cold. The swing
  without the split is if anything too small.
- **Continentality.** Not the cause. At 20-40 deg the bias is +2.1 on near-coastal land (smoothed land fraction
  < 0.4), +1.6 at 0.4-0.7 and +2.5 at 0.7-0.9. Interiors and coasts are alike.
- **Latitude band.** The excess is at 20-30 deg (+2.5) and 30-40 (+1.6): the subtropical deserts and the dry humid
  coasts. The heat goes where d_sum is +3.5 and more.
- **What's left is the split's own sensitivity on dry, sunny land.** The Sahara gets d_sum +7.6 C (+4.7 bias), N Mexico
  +6.8 (+2.6) and Arabia +6.4 (+0.8). 0.048 C per W/m2 is a 1500 m layer heated for a day, with no long-wave loss.

### Regions (warmest month bias vs NCEP, C; change from main with each swap)

| region | model / NCEP | bias | rain | LE | split off | annual bias | d_sum | LE W/m2 model / NCEP | sunshine model / CRU | rain mm model / GPCC |
|---|---|---|---|---|---|---|---|---|---|---|
| Sahara | 36.2 / 31.5 | +4.7 | +0.2 | +0.2 | -7.3 | +1.5 | +7.6 | 7 / 1 | 0.83 / 0.78 | 65 / 35 |
| Arabia | 34.7 / 33.9 | +0.8 | +0.5 | +0.4 | -6.4 | -2.0 | +6.4 | 17 / 5 | 0.76 / 0.73 | 250 / 97 |
| Mexico N | 28.3 / 25.7 | +2.6 | -1.3 | -1.1 | -6.5 | -1.9 | +6.8 | 13 / 43 | 0.88 / 0.62 | 199 / 482 |
| India | 33.3 / 32.6 | +0.7 | -2.0 | -1.8 | -3.6 | -0.8 | +3.3 | 46 / 84 | 0.53 / 0.49 | 627 / 1126 |
| SE USA | 30.4 / 25.3 | +5.1 | -1.1 | -2.8 | -1.8 | +2.2 | +1.1 | 66 / 133 | 0.42 / 0.65 | 719 / 1329 |
| Pampas | 31.5 / 25.1 | +6.4 | -1.6 | -2.2 | -2.9 | +1.7 | +3.1 | 43 / 89 | 0.53 / 0.65 | 394 / 943 |
| E Australia | 28.6 / 23.7 | +4.9 | -0.4 | -1.7 | -1.1 | +0.9 | +1.5 | 54 / 100 | 0.42 / 0.63 | 551 / 737 |
| SE China | 27.1 / 24.6 | +2.6 | -0.3 | -1.5 | +1.4 | +1.6 | -1.7 | 88 / 127 | 0.21 / 0.43 | 1061 / 1460 |
| NE USA | 24.2 / 21.3 | +2.8 | +0.7 | -0.6 | +2.5 | +2.4 | -3.5 | 107 / 112 | 0.17 / 0.56 | 1532 / 1033 |
| West Africa coast | 24.2 / 27.7 | -3.5 | +0.9 | +0.3 | +3.4 | -1.5 | -4.1 | 122 / 117 | 0.11 / 0.42 | 2539 / 1455 |
| Sahel | 27.7 / 31.6 | -3.9 | +1.9 | +2.1 | +1.6 | -3.0 | -2.3 | 105 / 61 | 0.21 / 0.63 | 2094 / 596 |
| US Southwest | 23.3 / 27.0 | -3.7 | +0.5 | +0.8 | -3.2 | -2.6 | +4.3 | 33 / 16 | 0.74 / 0.84 | 407 / 285 |

Every region of the 40 is in `diag/base.json` etc. (scratch). The full table can be re-made with `diag.py MODE` and
`summ.py`.

- **The dry humid coasts** (SE USA, Pampas, E Australia) are hot from three things:
  - an annual-mean bias of +1-2 C, which isn't the split;
  - half the observed evaporation: the LE swap removes 1.7-2.8 C, the rain swap 0.4-1.6;
  - the split's warming.
  - These are lane 120's dry coasts (PW-015). Their fix is the rain's supply round.
- **The hot deserts** (Sahara, Mexico N) are the split heating near-bare, sunny ground by 6.8-7.6 C.
- India is no hotter than NCEP. Its 33 C is right for April-May, Kolkata's 38 C aside.

## 4. Candidates (sources read in this lane)

Code: [candidates.patch](candidates.patch), two TUNE knobs in `planet/climate.py::_summer_split`. Both are off by
default. The split also gets the first pass's summer air and dew point (`planet/climate.py::_sum_air`).

### A. The finished frame's orbit at the seasons response (finish only)
- **Form.** `planet/finish.py::orbit_dt` builds the anomaly with `orbit_resp='seasons'`
  (`planet/timezoom/forcing.py::own_k` -> `planet/icemass.py::seasonal_k`), whatever the time zoom's ice rule is.
  No code in the patch: it's a one-line choice, and a decision (draft).
- **Source.** Braconnot et al. 2007, quoted in section 2. PW-459's own numbers: 0.078-0.088 C per W/m2 observed on
  40-70 N land.
- **Screen (dba204).** 0-20 deg 30.5 -> 25.2, 40-60 deg 22.7 -> 19.8, land >= 30 C 45.4% -> 19.0%, >= 35 C 18.1%
  -> 6.3%. Earth's earth_check and the runs don't see it: a run has no orbit_dt, and Earth's finish uses 'today'
  as the reference.

### B. Clear skies lose more long-wave (`split_lw`, FAO-56)
- **Form.** H gains -lw0 x (sun - sun_ref), with lw0 = sigma T^4 (0.34 - 0.14 sqrt(ea)) x 1.35/0.75 x 0.5. This is
  the part of FAO-56's net long-wave that changes with the sunshine between the cell and the reference, with Rs/Rso
  = (0.25 + 0.5 sun)/0.75. T and ea are the first pass's summer air and dew point.
- **Source.** Allen et al. 1998, FAO Irrigation and Drainage Paper 56, ch. 3, eq. 39 (read at fao.org/4/x0490e).
  - Rnl = sigma (Tmax,K^4 + Tmin,K^4)/2 (0.34 - 0.14 sqrt(ea)) (1.35 Rs/Rso - 0.35).
  - Rs/Rso runs from ~0.33 under dense cloud to 1 under a clear sky.
  - Its worked example gives Rs/Rso 0.77 -> a cloud factor of 0.69, which checks the 1.35 / 0.35.
  - The same form is already in `planet/climate.py::open_water_evap`.
- **Expected.** A sunny, dry cell's extra sunshine is offset ~40-50% by its extra long-wave loss, and an overcast
  one's deficit too.

### C. A hot, dry ground mixes a deeper boundary layer (`split_bl_max`, encroachment)
- **Form.** Where H = SW - LE (- B's term) beats the reference H_ref, the layer is sum_h x sqrt(H / H_ref) deep,
  capped at split_bl_max x sum_h. The warming per W/m2 falls by that factor. Encroachment growth gives h^2 in
  proportion to the day's integrated surface heat flux. Below the reference, the layer stays at 1500 m.
- **Source.** Ryder et al. 2015 (ACPD 15:199, Fennec aircraft overview; final ACP 15:8479), read here:
  - The Saharan atmospheric boundary layer "reaches to a height of 6000 m, generating what is commonly regarded to
    be the world's deepest boundary layer", "commonly reaching 5-6 km".
  - On one transect, warmer, drier air in the north leads to "a deeper CBL compared to the southeast (4 km at 24 N
    compared with 2 km at 21 N)".
  - Entrainment fluxes are "very weak". So the heat is spread over the depth, not lost through the top, which keeps
    a depth-scaling form honest.
  - The cap 4 = 6 km / 1.5 km.
- **Expected.** Deserts and dry subtropics warm about half as much per W/m2. Wet surfaces are unchanged.

### Earth L7 screens (diag.py base --tune; earth_check --level 7 on the private copies)

| | main | B (lw 1) | C (bl 4) | B+C |
|---|---|---|---|---|
| warmest month 0-20 deg (NCEP 26.5) | 24.6 | 24.8 | 24.4 | 24.7 |
| 20-30 deg (27.9) | 30.4 | 29.6 | 28.7 | 28.5 |
| 30-40 deg (22.8) | 24.4 | 23.5 | 23.3 | 22.9 |
| **20-40 deg (25.6)** | 27.7 (+2.1) | 26.9 (+1.3) | 26.3 (+0.7) | **26.0 (+0.4)** |
| 40-60 deg (18.5) | 18.3 | 18.5 | 18.2 | 18.4 |
| land >= 30 C (16.1%) | 17.8% | 16.8 | 15.2 | 14.5 |
| **land >= 35 C (1.7%)** | 7.9% | 4.9 | 1.5 | **0.7** |
| Sahara (31.5) | +4.7 | +2.9 | +1.4 | +0.7 |
| Mexico N (25.7) | +2.6 | +0.9 | +0.2 | -0.6 |
| SE USA / Pampas / E Australia | +5.1 / +6.4 / +4.9 | +4.8 / +6.0 / +4.8 | +4.4 / +5.6 / +4.7 | +4.3 / +5.4 / +4.6 |
| Arabia / India / US Southwest | +0.8 / +0.7 / -3.7 | -0.7 / -0.1 / -4.6 | -2.1 / -1.3 / -4.7 | -2.6 / -1.5 / -5.3 |
| Köppen B % (Kottek 30.1) | 25.0 | | 24.7 | 24.6 |
| BWh % (14.8) | 12.9 | | 12.0 | 11.7 |
| exact / group % | 37 / 70 | | 37 / 70 | 37 / 71 |
| log-rain r | 0.714 | | 0.714 | 0.714 |
| point check exact / group / wrong | 37 / 21 / 20 | | 37 / 21 / 20 | 37 / 21 / 20 |

- Both move the right way. C does most of the work, and B+C brings the 20-40 deg excess from +2.1 to +0.4 and the
  >= 35 C land from 7.9% to 0.7% (NCEP 1.7%).
- **Costs.**
  - Arabia (-2.6), India (-1.5) and the US Southwest (-5.3, which was already cold) go cool.
  - Köppen B -0.4 points, the wrong way: cooler deserts have a lower PET, against an already 5-point B deficit.
- The humid coasts hardly move (-0.8 to -1.0). They need their rain.
- B+C overshoots the >= 35 C tail (0.7% against 1.7%). C alone (1.5%) is closest there.

### L6 seeds, 1 Gyr (main vs B+C; land climate sanity)

See section 5.

## 5. L6 seeds

- **Harness.** `seeds.sh`: `planet simulate --level 6 --myr 1000` for seeds 1 and 2, main against B+C (split_lw 1,
  split_bl_max 4), on scratch stores. `simtune.py` applies the TUNE overrides in-process, because health.py's
  workers are spawned and wouldn't see them.
- **Measures.** `runs_measure.py`: means over the keyframes from 800 to 1000 Myr. The warm month is the larger of the
  July and January layers (1 C steps), over ice-free land. The main runs reproduce lane 120's main late dT (2.3 and
  6.1).

| seed | arm | run | late dT C | arid (Köppen B) % | land >= 30 C % | land >= 35 C % | warm month 0-20 / 20-40 / 40-60 deg |
|---|---|---|---|---|---|---|---|
| 1 | main | 6c3fe6 | 2.3 | 23.2 | 18.0 | 5.7 | 25.6 / 28.1 / 18.5 |
| 1 | B+C | 5581df | 0.8 | 25.8 | 14.8 | 1.8 | 24.2 / 24.8 / 17.6 |
| 2 | main | c9a677 | 6.1 | 27.3 | 32.2 | 14.4 | 27.7 / 32.3 / 21.6 |
| 2 | B+C | 7dfee8 | -0.7 | 20.2 | 5.7 | 0.3 | 23.7 / 24.2 / 15.7 |

- **The hot tail goes.** The >= 35 C land falls 5.7 -> 1.8% and 14.4 -> 0.3%, and 20-40 deg cools 3-8 C. Part of
  that is the late dT, so it isn't a fixed-climate comparison. Earth L7 (section 4) is the fixed-dT one.
- **The late dT falls on both seeds:** -1.5 C on seed 1, and -6.8 on seed 2.
  - Seed 2 is a known flipper: lane 120's friction arm took it 6.1 -> -0.1 too. Two seeds can't separate a
    systematic cooling from that chaos (memory: compare over re-rolled draws).
  - A plausible systematic path: cooler dry summers give a lower PET, so more runoff and more weathering, so less
    CO2.
  - It needs a re-rolled multi-seed set before any merge.
- **Arid share.** +2.6 on seed 1 (at a cooler dT), -7.1 on seed 2 (a colder world). There's no clear sign.

## 6. Recommendation

1. **dba204, which is what the owner saw: decide the finished frame's orbit response first** (needs-decision draft
   [draft-finished-frame-orbit-response-too-strong](../../../../issue-tracking/inbox/draft-finished-frame-orbit-response-too-strong.md)).
   - Option A, `planet/finish.py::orbit_dt` on the 'seasons' response, removes ~5 C of the 0-20 deg July and 26
     of the 45 points of land >= 30 C.
   - It is a one-line change. It doesn't touch the ice, the runs or Earth, and it is sourced (Braconnot et al.
     2007; PW-459's own measurement).
   - That alone answers "is dba204 aberrant": yes, and this is why.
2. **The base climate's subtropical heat is the summer split. It's sound to fix, but not alone.**
   - B+C (deep dry layer plus clear-sky long-wave) takes Earth's 20-40 deg excess from +2.1 to +0.4 C and its
     >= 35 C land from 7.9% to 0.7%, at -0.4 points of Köppen B.
   - It overshoots on Arabia, India and the US Southwest.
   - It cools both L6 seeds' late dT (-1.5, and -6.8 on the flipper seed 2).
   - The split's reference is on the sky-cover scale, and the overcast-tropics bug
     ([draft-summer-split-overcast-tropics](../../../../issue-tracking/inbox/draft-summer-split-overcast-tropics.md))
     has to move it to CRU's sunshine scale. So my lean is one round:
     - re-anchor the reference;
     - re-screen B+C on it;
     - then a re-rolled multi-seed set for the dT drift, before the 36-world judge
       ([draft-summer-split-deep-dry-boundary-layer](../../../../issue-tracking/inbox/draft-summer-split-deep-dry-boundary-layer.md)).
   - No merge from this lane.
3. **The dry humid coasts** (SE USA +5.1, Pampas +6.4, E Australia +4.9) are the rain's (PW-015, back of the line).
   - Their observed evaporation would take 1.7-2.8 C off. The observed rain through Budyko takes 0.4-1.6.
   - They keep a +1-2 C annual-mean bias of their own.
   - The PW-1322 draft has these numbers.
4. **Three strikes doesn't apply.** All three candidates moved the warm month the right way.
