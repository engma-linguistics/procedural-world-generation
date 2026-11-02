# Lane 125: tropical cloud and cool winters (PW-1330, PW-1327). Diagnosis only, 2026-11-02

Status: **diagnosis only; no model change.** Main after 994e82d2. Harness: [bands.py](bands.py) (tables),
[components.py](components.py) (which cloud kind makes the cover). Earth model climate = `vegetation.coupled_climate` at
L7 on a private copy of data/earth (L7.npz, clouds_L7.npz; the real data/earth was only read). Finished worlds read
from the shared worlds/ (read-only). Outputs not kept (scratch deleted).

## In plain words

- **The worlds' cloudy semi-arid tropics are not a world problem: the Earth model is cloudy in just the same way.**
  Put Earth through the model and its warm land at 400-900 mm has shade 0.40 against 0.27 observed *in the same cells*;
  the five worlds I looked at have 0.38-0.44. The worlds are no cloudier than the Earth model is. PW-1330's "0.29 on
  Africa" is the observed number; the model never reaches it, on Earth or elsewhere.
- **Where the cloud comes from:** the land's "humidity layer cloud" (`cloud_rh` x relative humidity^1.5, written for
  winter stratus over Europe) is the biggest single piece over warm tropical land. Switch it off and the 400-900 mm
  shade falls from 0.41 to 0.25 (observed 0.27-0.31). It reads the air mass's humidity, which in warm tropical air is
  high all year, so it paints a stratus deck that savannas do not have. The second piece is the rain-belt deep cloud
  (about 0.1 of shade at 400-900 mm, 0.14 above 900).
- **The cool coldest months are a different cause and not a cloud one.** Clouds don't touch temperature except through
  the summer split (`_summer_split`, summer only), so the coldest month can't come from the cloud. On Earth itself the
  model's coldest month is 1.6-2.7 C below NCEP in the same cells (13.7 vs 16.4 C at 400-900 mm), and the mean
  temperature is 1-2 C low too. The worlds scatter around the Earth model's value (14.2-19.6 C at 400-900 mm, section 2).
  That belongs with the winter-air work (PW-026 family), not with cloud.
- **PW-1327 is real and separate, but the same cloud scheme sits underneath.** The summer heat split reads sky
  cover where it should read sunshine. Reading the sunshine share (which already has the afternoon-showers discount)
  moves the wet tropics from 0.12-0.22 to ~0.35-0.45, still short of CRU 0.46-0.57 because the cloud itself is too
  thick (point above). So fixing the reading alone only gets part way; fixing the cloud alone makes the split's cell
  and its reference (0.63 sky cover) disagree. They want one change.
- **Sky cover vs sunshine is conflated in four more places** (next section). Only the first two matter for the tropics.

## 1. Earth model vs observed, same cells

Warm land (observed annual T > 18 C), |lat| < 35. Shade = `climate.shade(sunshine share)`, the cover the day's light
sees (observed shade is from CRU sunshine by the same map); sky = cloud cover (observed: NCEP total cloud, a
reanalysis, so only roughly); sun = sunshine share of possible hours; Tc = coldest month. Rows "same cells" keep cells
whose rain falls in the band in BOTH the model and GPCC, because the Earth model's own rain geography is badly off in
exactly these regions (Sahel model median 2609 mm vs 530 observed; East Africa 2577 vs 625; PW-rain-inland's known
bias), so banding by model rain alone compares different places.

| rain band | | n | sky | sun | shade | Tc (C) | MAT |
|---|---|---|---|---|---|---|---|
| 400-900 | model | 515 | 0.46 | 0.59 | **0.40** | 13.7 | 20.8 |
| | observed | | 0.34 | 0.71 | **0.27** | 16.4 | 22.6 |
| 900-1500 | model | 702 | 0.64 | 0.46 | **0.55** | 18.4 | 22.1 |
| | observed | | 0.49 | 0.58 | **0.41** | 20.0 | 23.2 |
| >1500 | model | 3945 | 0.80 | 0.33 | **0.69** | 22.6 | 23.7 |
| | observed | | 0.68 | 0.47 | **0.53** | 22.8 | 23.9 |

Model-rain banding (as the worlds are banded; not the same places as the observed row):

| 400-900 / 900-1500 / >1500 | n | shade | Tc | Twarm |
|---|---|---|---|---|
| Earth model | 2522 / 2539 / 8116 | 0.41 / 0.55 / 0.62 | 14.7 / 18.8 / 21.3 | 28.9 / 26.4 / 24.5 |
| Earth observed (obs rain) | 3419 / 4426 / 5659 | 0.30 / 0.41 / 0.53 | 18.5 / 20.0 / 22.0 | 28.7 / 26.7 / 25.3 |

**Regions, 400-900 mm** (masked by observed rain and observed T, model vs observed; the model's own rain there is
2-3x too high in the Sahel and E Africa, so read "model" as "what the model's climate puts on those places"):

| region | n | shade model / obs | sun model / obs | Tc model / obs | Twarm model / obs |
|---|---|---|---|---|---|
| Sahel (10-16N) | 481 | 0.38 / 0.28 | 0.61 / 0.69 | 19.8 / 22.5 | 27.8 / 31.8 |
| E Africa (5S-5N, 34-42E) | 167 | 0.80 / 0.32 | 0.23 / 0.66 | 20.6 / 20.8 | 21.8 / 25.0 |
| S Africa savanna (25-10S, 15-35E) | 562 | 0.46 / 0.27 | 0.54 / 0.71 | 12.7 / 15.2 | 22.8 / 26.5 |
| India (10-28N, 72-88E) | 262 | 0.29 / 0.35 | 0.69 / 0.63 | 15.1 / 19.2 | 33.0 / 33.2 |
| N Australia (20-11S, 125-145E) | 279 | 0.47 / 0.21 | 0.53 / 0.76 | 17.7 / 19.2 | 27.0 / 31.4 |
| Brazil cerrado (20-8S, 55-42W) | 77 | 0.68 / 0.36 | 0.34 / 0.62 | 20.5 / 21.7 | 23.9 / 25.5 |

(India is the only region where the model is *clearer* than CRU, and there its rain is too low, 530 mm at the
observed 900-1500 band. Everything with too much model rain is too cloudy: E Africa and the cerrado worst.)

Regions in the matched-cells rows (n small): Sahel 0.38 vs 0.29, S Africa 0.42 vs 0.27, N Australia 0.40 vs 0.19,
India 0.40 vs 0.35 (400-900); N Australia 0.55 vs 0.30, S Africa 0.56 vs 0.33, cerrado 0.57 vs 0.40 (900-1500).

## 2. Three finished L7 worlds (plus two more)

Same bands, |lat| < 35, warm land (T > 18), banded by each world's own rain; shade from the stored sunshine layers.

| world | band | n | sky | sun | shade | Tc | Twarm |
|---|---|---|---|---|---|---|---|
| dba204 | 400-900 | 4545 | 0.44 | 0.61 | 0.38 | 16.8 | 29.2 |
| | 900-1500 | 3357 | 0.56 | 0.53 | 0.47 | 16.1 | 30.1 |
| | >1500 | 13645 | 0.70 | 0.42 | 0.58 | 18.0 | 31.5 |
| 899985 | 400-900 | 4664 | 0.44 | 0.61 | 0.38 | 19.6 | 29.0 |
| | 900-1500 | 2478 | 0.62 | 0.48 | 0.52 | 22.0 | 29.2 |
| | >1500 | 13936 | 0.78 | 0.35 | 0.66 | 23.6 | 29.0 |
| 1df1c3 | 400-900 | 2190 | 0.49 | 0.57 | 0.43 | 18.7 | 26.9 |
| | 900-1500 | 2381 | 0.60 | 0.49 | 0.51 | 18.9 | 27.7 |
| | >1500 | 13041 | 0.70 | 0.41 | 0.60 | 21.6 | 26.1 |
| 6909cb | 400-900 | 2839 | 0.47 | 0.59 | 0.40 | 14.2 | 32.5 |
| | 900-1500 | 2775 | 0.61 | 0.48 | 0.52 | 17.3 | 30.1 |
| | >1500 | 13583 | 0.76 | 0.36 | 0.66 | 23.5 | 27.7 |
| 3e9e7d | 400-900 | 2993 | 0.51 | 0.55 | 0.44 | 16.3 | 28.3 |
| | 900-1500 | 2952 | 0.57 | 0.53 | 0.47 | 15.1 | 31.5 |
| | >1500 | 8012 | 0.72 | 0.41 | 0.60 | 18.2 | 31.5 |

Against the Earth model (shade 0.41 / 0.55 / 0.62) the worlds are 0.38-0.44 / 0.47-0.52 / 0.58-0.66: **the same, and
if anything slightly clearer at 900-1500.** Coldest month 14-20 C at 400-900 mm (Earth model 14.7, Earth observed 18.5):
the worlds are as cool as the Earth model, and the scatter between worlds (14-20) is climate geography, not cloud.
The dba204 warmest month (29-31.5) is the orbit effect lane 121 found, not cloud.

## 3. How the cloud is made, which kind does it

`planet/climate.py::clouds` builds cover from four kinds overlapping at random: deep (`cloud_deep` 0.8, grows with the
300-km-smoothed rain above 300 mm/yr), storm-track layer cloud (`cloud_storm` x storminess), land humidity layer cloud
(`cloud_rh` 0.55 x rh^1.5, plus the Sc deck drifting inland), fair-weather cumulus (`cloud_cu` 0.5), cleared by
subtropical sinking air (`cloud_clear` 0.5 x exp(-rain/800)). It returns (cover, `sunshine(cover(cloud_sun_conv=0.6))`,
so deep and cumulus count at 0.6 of the day, layer cloud whole). `climate.shade` inverts that for the plants.

Drop-one on warm land, sky / shade, by band (400-900 | 900-1500 | >1500 mm; `components.py`, re-solved climate):

| | Earth model | dba204 |
|---|---|---|
| all kinds | 0.48/0.41, 0.65/0.55, 0.73/0.62 | 0.46/0.39, 0.62/0.53, 0.71/0.61 |
| no humidity layer cloud (`cloud_rh`, `cloud_polar`) | 0.36/**0.25**, 0.53/**0.37**, 0.63/**0.45** | 0.33/0.23, 0.51/0.36, 0.62/0.44 |
| no deep | 0.36/0.32, 0.49/0.44, 0.56/0.49 | 0.33/0.30, 0.46/0.41, 0.54/0.47 |
| no cumulus | 0.44/0.37, 0.61/0.51, 0.69/0.57 | 0.43/0.36, 0.58/0.48, 0.67/0.56 |
| no storm layer | 0.46/0.38, 0.64/0.54, 0.72/0.61 | 0.44/0.37, 0.61/0.51, 0.70/0.59 |
| no subtropical clearing | 0.54/0.46, 0.69/0.59, 0.74/0.64 | 0.51/0.44, 0.66/0.56, 0.73/0.62 |

Observed shade 0.27-0.31 / 0.41 / 0.53. So the humidity layer cloud alone is worth 0.16 / 0.18 / 0.17 of shade, more than
the whole gap (0.10-0.13 / 0.14 / 0.09-0.16). The land's `rh` is the air mass's mean humidity (`vapour_mixed`), which
over warm land is high (it only drops in dry-season continental interiors), so rh^1.5 x 0.55 = 0.2-0.4 of constant
stratus. (Unsourced hunch, not read anywhere: savanna cloud is mostly convective, which the scheme has as deep+cumulus;
with those two off, shade is 0.27-0.36 from the humidity and storm terms alone.) Whether `cloud_rh`
is also what makes W Europe pass (PW-162/232 history: tuned on W Europe 60-75%) is the constraint on cutting it for warm
air. Observed-side caveat: CRU CL 2.0's sunshine in the tropics is sparse-station data; I did not establish how much of
it is cloud-derived (the CRU TS 2.0 intro says cloud was anomalised with sunshine, the reverse direction), so the
0.27-0.31 could be 0.05 off. The NCEP cloud column agrees in direction (model sky 0.46/0.64/0.80 vs NCEP 0.34/0.49/0.68).

## 4. Where sky cover and sunshine are conflated

`months(cloud_jul, cloud_jan)` expects the light's cloud (shade, per its docstring). Callers:

| place | passes | right? |
|---|---|---|
| `planet/world.py` ~130, 214, 217 (plants, soils) | `c["shade_*"]` | yes (PW-808 fix, be00f07) |
| `planet/climate.py::_summer_split` call (~2631) | `np.where(north, cloud_jul, cloud_jan)`, **sky cover** | **no** (PW-1327): `sunshine(sky)` 0.12-0.22 in the wet tropics vs CRU 0.46-0.57 |
| `planet/climate.py::open_water_evap` call (~2700) and `planet/nest.py` (~170) | `cloud_jul/jan` sky | **no**: lake Penman radiation reads sky through `sunshine()`; the lake's net radiation is low in the wet tropics, so lake evaporation is low there (not measured here) |
| `planet/server.py` cell inspector (~330) | `c["cloud_jul"]/100` sky into `months` | **no**, display only (the monthly chart shown for a cell differs from the one the plants saw) |
| `planet/vegetation.py::model(sky=)` | sky, for montane cloud forest | intended |
| `planet/soils.py::_climate`, `world.py` soils/vegetation | shade | yes |

Not conflated: `tools/earth_check.py::earth_clouds` compares `sun_*` to CRU and `cloud_*` to NCEP/ICOADS correctly.
`climate.compute` temperature does not read the cloud anywhere else (clouds are diagnostic since PW-163).

## 5. Causes

1. **`cloud_rh` land humidity layer cloud is too heavy over warm moist land** (~0.16-0.18 of shade, all of the
   gap). Present on Earth and on every world; it is the same on Earth, not a world effect. (PW-1330 cloud half.)
2. **The Earth model's rain is 2-3x too high in the semi-arid tropics** (Sahel, E Africa, cerrado), which feeds the
   deep cloud and the humidity: the worst shade gaps are where the rain is worst (E Africa 0.80 vs 0.32). Rain, not
   cloud code; already PW-rain-inland territory.
3. **`_summer_split` reads sky cover** (PW-1327), so wet tropics read too cloudy in a second, independent way, and
   its reference (`cloud_ref` 0.63) is on the same sky-cover scale.
4. **Cool coldest month: not cloud.** Model winter air / the temperature curve, 1.6-2.7 C low at 400-900 mm on Earth.
   Open question whether the sunshine-split's summer cooling, the lack of a dry-season warmth, or the winter-air work
   is the lever; I did not diagnose it (needs its own lane, with the PW-026 family).

## 6. Candidate fixes (none tried)

A. **Make the land humidity cloud convective-aware.** Give `cloud_rh` a warm-air discount: the layer-cloud term
   `cloud_rh * rh^1.5` scaled down where the season's sea-level temperature is high (stratus belongs to cool, stable
   air). Cheapest check: re-run `components.py` with the term scaled by (1 - k * clip((t_sl - 15)/10, 0, 1)) and watch
   the 400-900 / 900-1500 / >1500 shade (target 0.30 / 0.41 / 0.53) *and* W Europe, the Pacific NW and Siberia
   (the cloud regions it was written for, `tools/earth_check.py::CLOUD_REGIONS`). Source for the premise: this repo's
   own tables above (drop-one) and the repo's docstring at `climate.py::clouds`; I have no external source for the
   stratus-vs-convective split and did not look for one, so the physical argument needs a paper before a ticket
   relies on it.
B. **Feed `_summer_split` the sunshine, not the sky** (PW-1327's sketch; a pure reading fix). `climate.py::clouds`
   already returns it (`sun_jul/sun_jan`, with `cloud_sun_conv`). The code change is `sunshine(cloud_sum)` ->
   the returned share in `_summer_split`, and `cloud_ref` -> a sunshine reference (0.38 = CRU land 20-60 deg summer
   0.62 per PW-1327 / lane 121's table, which I read in docs/review/base-climate/summer-heat/diagnosis.md). Lane 121
   measured the CRU swap alone: +0.3 C 20-40 deg, +1.7 C 40-60 deg, so the reference move is required. Do it after
   A (otherwise it fixes the reading but not the cloud).
C. **Lake and display readers**: `open_water_evap` (climate.py ~2700, nest.py ~170) and the server's cell inspector
   take the light's shade like the plants. The Ångström-Prescott relation Rs = (as + bs n/N) Ra is in terms of
   relative sunshine duration n/N, i.e. sunshine, not sky cover (FAO-56 chapter 3, Allen et al. 1998,
   https://www.fao.org/4/x0490e/x0490e07.htm, fetched; defaults as=0.25, bs=0.50 "will vary" with humidity, dust,
   latitude and season), so a sunshine input is the relation's own. Measure Lake Victoria / Amazon floodplain
   evaporation before and after (PW-358's table: 1415 / 1406 mm) before merging.

Order: A then B then C, one ticket (the split's reference and the cloud move together). The cold-winter cause is a
separate ticket.

## Files

[bands.py](bands.py), [components.py](components.py). Inputs read: docs/review/base-climate/summer-heat/diagnosis.md
and diag.py, docs/review/vegetation/npp-check/diagnosis.md and inputs_cmp.py, docs/review/base-climate/v1-finish-12/README.md,
PW-143/162/163/358/808, planet/climate.py, planet/world.py, planet/nest.py, planet/server.py, tools/earth_data.py.
