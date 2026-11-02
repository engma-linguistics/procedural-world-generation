# Lane 131: tropical cloud round 2, diagnosis (PW-1347, PW-1348, PW-1335), 2026-11-02

Status: **diagnosis only. Nothing merged, nothing committed under planet/.** Base: main afed2ced (lane 126 merged).
Earth L7 only (`vegetation.coupled_climate` on a private copy of data/earth in the worktree; data/earth was only read).
No L6 runs. Harness (this folder): [screen2.py](screen2.py) (lane 126's screen.py measures, plus coldest month by band,
the winter breakdown, the cloud pieces by region and half-year, the sea next to W Central Africa),
[winter2.py](winter2.py) (offline breakdown of the coldest-month miss and of the 20-40 deg sunshine excess),
[ec2.sh](ec2.sh) (screen2.py + `tools/earth_check.py` per arm, TUNE overrides through [withtune.py](withtune.py)),
[table2.py](table2.py) (the table below). Code candidates: [round2.patch](round2.patch) (TUNE knobs, all off by default;
not applied to planet/; arms that set `cloud_rh_floor`, `cloud_inland_km`, `cloud_seastab_km` or `mee_k` need
`git apply round2.patch` first).

## In plain words

- **Congo (PW-1347): leave the gate alone; the missing cloud comes from the sea, and the model's sea there is too
  warm.** The real dry-season (June-September) cloud over Gabon and the western Congo is a low stratus deck. Cool
  air off the south-east Atlantic blows inland under warm air aloft, so the air is stable. It is thickest on the
  coastal plains and thins inland. Deeper in the Congo basin the dry season is the *sunniest* time of year. The
  model's sea off Gabon in July is 25.8 C. NCEP's air over that sea in its coldest month is 23.7 C. So the model sees no
  inversion there (air aloft only 1.3 C warmer than the sea), and the sea has no deck to blow inland. Two
  coast-to-inland candidates (carry the deck inland, carry the sea's stability inland) did nothing for that reason. The
  gate floor gets 63% of the 70-80%. Three strikes. The fix belongs to the ocean (the cold-season eastern equatorial
  Atlantic), not the cloud: draft.
- **Summer subtropics too sunny (PW-1348): it is the rain. Leave it.** 70% of the 20-40 deg summer sunshine excess
  sits on land where the model's rain is under 0.6 x GPCC (a third of the band's land). Where the rain is within 20%,
  the excess is +0.08. India and N Mexico get monsoon rain the model doesn't make. A 30% gate floor or more cumulus
  takes only 0.02-0.03 off the band. Both make the wet tropics darker than CRU and W Europe / the Pacific NW cloudier.
- **Cool winters of warm semi-arid land (PW-1335): about a third of it is height, the rest is a missing dry-season
  warmth.** The model's coldest-month miss grows with the ground's height, about -1.5 C per km (all latitudes). The
  observed field is already brought to each cell's height with the model's own 6.5 C/km, so this is not the
  data's terrain. Real high plateaus are warmer than the free air at the same height (the "mass elevation effect":
  ~5 K at 3700 m on the Altiplano, He et al. 2016). Adding that effect at 1.35 C per km of plateau height (the Altiplano
  figure) fixes the 20-40 deg coldest month (-1.6 -> -0.6 C) and cuts Köppen E (11.7 -> 10.4%, Kottek 7.3%). But the
  semi-arid cells' winter moves only from 13.8 to 14.3 C (NCEP 16.4), and the 40-60 deg winters get too mild (+1.0 ->
  +1.9 C). It also pulls 50% more rain into the Congo (sky up for the wrong reason). On low ground with the right rain,
  the winter is still 1.6 C cold while the summer is right. That fits a missing *winter* energy split: the model warms
  dry, sunny summers but not dry, sunny winters. Not screened (strikes used on the height arms): draft. Recommended:
  none of the three to merge as is; height effect worth a ticket with an ice check.

## 1. Sources read in this lane

- **Champagne et al. 2023**, "Climatology of low-level clouds over western equatorial Africa based on ground
  observations and satellites", J. Climate 36, doi 10.1175/JCLI-D-22-0364.1 (KIT open PDF, full text read). Abstract:
  "an extensive and persistent low-level stratiform cloud deck during the long dry season from June to September
  (JJAS)"; "low-level clouds persist during the day over the coastal plains and windward side of the low mountain
  ranges. Conversely, on their leeward sides, i.e., over the plateaus, a decrease of the low-level cloud frequency is
  observed in the afternoon, together with a change from stratocumulus to cumulus." Body: low clouds "decrease inland,
  likely associated with a foehn effect leeward of the Chaillu Mountains, Cristal Mountains, and Batéké Plateau";
  "particularly so in boreal summer, when the coastal upwelling extends northward to Cape Lopez (0°37'S) and the
  equatorial upwelling cools the eastern equatorial Atlantic Ocean"; "the years with very warm sea surface
  temperatures in the eastern Atlantic favored less stratiform clouds in Gabon (Maley and Hilaire 1993)".
- **Berger et al. 2025**, "The dry-season low-level cloud cover over western equatorial Africa: A case study with a
  mesoscale atmospheric model", QJRMS e4962, doi 10.1002/qj.4962 (KIT open PDF, abstract read): "The LCC persistence is
  associated with surface westerlies advecting cooler maritime air increasing the lower-tropospheric stability."
- **Philippon et al. 2019**, "The light-deficient climates of western Central African evergreen forests", Environ.
  Res. Lett. 14:034007 (IOP article page; read through a fetch summary with short verbatim quotes, not the whole
  text): "a uniform and opaque cover of low-level stratiform clouds in June–September"; in SW Gabon direct irradiance
  "below 80 W m−2 in JJAS"; "further inland the main dry season is, as usually expected, the brightest season".
- Dommo et al. 2018 (J. Climate; low cloud of W Central Africa, JJAS): **seen only as a search-engine abstract
  snippet**, not read: "WCA cloud cover is dominated by single-layered low stratiform clouds", the west-to-east decline
  "related to a foehn effect". Not relied on beyond what Champagne 2023 says.
- **He et al. 2016**, "The mass elevation effect of the central Andes and its implications for the Southern
  Hemisphere's highest treeline", Mountain Res. Dev. 36:213-221 (BioOne page, abstract + intro excerpt read): "The mean
  air temperature in the Altiplano in summer is approximately 5 K higher than it is above the adjacent lowlands at the
  same mean elevation, averaging about 3700 m above sea level"; mechanism (their intro, citing Flohn 1953 and others):
  "The elevated plateau surfaces receive more radiation, and serve as a heating surface absorbing solar radiation and
  transferring the heat to the atmosphere". In July (winter) 10 of 15 stations were positive, and the difference
  "increased from high latitudes to low latitudes in winter". Search-snippet only, not read: Yao & Zhang 2015 (Tibet,
  3.6-6.6 K at 4500 m by month).
- Lane 126's sources (Klein & Hartmann 1993, Eastman & Warren 2014, Cermak et al. 2009) as cited in
  [round1.md](round1.md); not re-read.

## 2. PW-1347: the Congo's low cloud

**What makes it.** `planet/climate.py::clouds` + `::_layer_gate`. The CLOUD_REGIONS Congo box (5S-5N, 12-30E) is
annual 59.6% (70-80), July 53% / January 67%. Pieces by half-year (screen2.py "components"; land, as run):

| half, region | lts C | gate | rh | layer | deep | cu | sky | sun model / CRU | NCEP sky | model rain mm/yr |
|---|---|---|---|---|---|---|---|---|---|---|
| Jul, Congo box | -2.1 | 0.08 | 0.71 | 0.02 | 0.45 | 0.12 | 0.53 | 0.62 / 0.44 | 0.67 | 1231 |
| Jul, Gabon / W Congo (5S-2N, 9-16E) | -1.2 | 0.16 | 0.51 | 0.03 | 0.21 | 0.00 | **0.26** | **0.78 / 0.33** | 0.68 | 366 |
| Jan, Congo box | -2.1 | 0.07 | 0.79 | 0.02 | 0.58 | 0.22 | 0.67 | 0.53 / 0.46 | 0.69 | 2240 |
| Jul, Amazon (for comparison) | +0.1 | 0.36 | 0.86 | 0.15 | 0.61 | 0.30 | 0.75 | 0.43 / 0.48 | 0.72 | 2347 |

The miss is the July (dry-season) half, and it is worst in Gabon / W Congo, exactly where the sources put the stratus
deck (sun 0.78 vs CRU 0.33). The box's annual rain is right (1735 vs GPCC 1653), so this is **not** the rain.

**Why the model can't make it.** The sources' mechanism is cool, stable maritime air from the SE / equatorial Atlantic
advected inland under the dry-season westerlies (Berger 2025; Champagne 2023). The model has the right *kind* of rule
for that over the sea (`cloud_sc` deck under a strong inversion, drifting one cell onto a low coast). But next to
Gabon its sea gives it nothing to work with:

| sea, July half | model deck | t_ref - sst C | model sst (Jul) | model sst annual | NCEP 2 m air annual / coldest month |
|---|---|---|---|---|---|
| off Gabon (5S-2N, 4-9E) | 0.01 | +1.3 | 25.8 | 26.0 | 26.0 / 23.7 |
| off Angola (17-5S, 6-12E) | 0.34 | +3.3 | 23.2 | 24.5 | 23.4 / 20.4 |
| E equatorial Atlantic (3S-3N, 15W-5E) | | | 25.3 | 25.3 | 26.0 / 23.9 |

(NCEP air over the sea is only a rough stand-in for the water's temperature.) The model's eastern equatorial Atlantic
hardly cools in its cool season (25.8 vs ~23.7). That is the equatorial and coastal upwelling the sources name. Also
the subtropical sinking (`sink`) that the deck needs is ~0.03 at 0-5 S. So the model has no inversion and no deck off
Gabon. And the model's Gabon air is dry (rh 0.51; Philippon cites ~90% maximum humidity, not the same quantity).

**Is it a floor on the gate, convective cloud, rain, or something else?** Something else: a stable marine stratus
whose stability comes from a cool sea upwind. A gate floor is the wrong physics (it adds stratus to *all* unstable
warm land). Deep convective cloud is the wrong kind (the sources say single-layer stratiform, dry season). Rain is right.

**Candidates (code in round2.patch):**

| arm | Congo sky % (70-80) | Gabon-W Jul sky / sun (CRU .33) | shade bands (obs .27/.41/.53) | summer sun 0-10 (CRU .46) | other |
|---|---|---|---|---|---|
| main | 59.6 | 0.26 / 0.78 | .31/.42/.54 | .395 | |
| a. gate floor 0.3 (`cloud_rh_floor`, lane 126's untried) | 63.0 | 0.30 / 0.74 | .33/.46/.58 | .351 | Pacific NW 83 (60-75), Amazon 82.6 (65-80) |
| b. sea deck carried inland, e-fold 200 / 400 / 800 km (`cloud_inland_km`, re-call only) | 60 | 0.26 / 0.78 | unchanged | unchanged | no effect: no deck off Gabon to carry |
| c. sea inversion carried inland for the gate, e-fold 150-600 km (`cloud_seastab_km`; full solve at 300) | 59.6 | 0.26 / 0.78 | unchanged | .395 | no effect: t_ref - sst only +1.3 C off Gabon |

(A first version of c took max(land lts, sea lts) and so put a floor of lts = 0 on all land. That made it the same as a
floor of 0.33. Fixed to max(lts, carried - cloud_rh_lts[0]) before the screen in the table. Mentioned only so the
re-call log in the scratch isn't misread.)

**Recommendation: leave the gate.** Three strikes on this ticket. Re-measure c once the eastern equatorial / Benguela
cold season is in the sea (draft `draft-east-equatorial-atlantic-cold-season-too-warm`). Note the 70-80% range is
for a box whose eastern two-thirds is, per Philippon 2019, sunniest in the dry season. The range may be too high for
the box's July half. That is a target judgement, not something to change here (no threshold loosening).

## 3. PW-1348: summer 20-40 deg land too sunny

**What makes it.** `planet/climate.py::_layer_gate` sends the layer cloud to ~0 over summer land at 20-40 deg (lts
-5 to -8 C: India -5.3, N Mexico -8.0, W Europe -5.7, SE USA -5.3). What's left is deep cloud from the rain, cumulus,
and the subtropical clearing (`cloud_clear`). Where the rain is too low, that is very little:

| July half | gate | deep | cu | clear | sky | sun model / CRU | model rain (half-year rate) / GPCC annual |
|---|---|---|---|---|---|---|---|
| India (10-28N, 72-88E) | 0.00 | 0.30 | 0.19 | 0.13 | 0.38 | 0.71 / 0.49 | 981 / 1126 (annual 626) |
| Mexico N (24-31N, 110-100W) | 0.00 | 0.00 | 0.01 | 0.36 | 0.02 | 0.94 / 0.61 | 103 / 490 (annual 203) |
| W Europe | 0.01 | 0.25 | 0.33 | 0.01 | 0.57 | 0.56 / 0.45 | 758 / 903 |
| SE USA | 0.02 | 0.38 | 0.32 | 0.18 | 0.49 | 0.66 / 0.64 | 1014 / 1350 |

**Where the excess sits** (winter2.py; ice-free land 20-40 deg, model summer sunshine 0.758 vs CRU 0.669):

| model annual rain vs GPCC | share of band area | sunshine excess | share of the band's excess |
|---|---|---|---|
| < 0.6 x | 32% | +0.196 | **70%** |
| 0.6-0.8 x | 14% | +0.103 | 16% |
| within 20% | 22% | +0.076 | 18% |
| > 1.2 x | 32% | -0.014 | -5% |

**Physics.** Eastman & Warren 2014 (lane 126, read there) has summer continental cloud dominated by cumulus and
cumulonimbus. So the gate removing the layer is right, and the sunshine should come back as convective cloud from the
monsoon rain (India's and Mexico's July is their wet season). The missing piece is the rain itself (PW-1349 and the
rain-inland work, parked under three strikes). Not a floor. W Europe's +0.11 has right-ish rain. That is the one
place a cloud cause remains: the convective clouds count at `cloud_sun_conv` 0.6 of the day, and the summer
storm-track cloud is thin there (storm 0.17). I did not chase it (it is 1 region, and the rain-right cells' excess is
+0.08).

**Candidates (full solves; table in section 5):**

| arm | summer sun 0-10 / 10-20 / 20-40 / 40-60 (CRU .46/.57/.67/.55) | W Eur / India / Mex N sun | side effects |
|---|---|---|---|
| main | .395/.477/.758/.520 | .56/.71/.94 | |
| a. gate floor 0.3 | .351/.437/.732/.495 | .53/.68/.92 | wet tropics darker (0-10 .35 vs .46); shade >1500 .58 vs .53; PNW sky 83 |
| b. more cumulus, `cloud_cu` 0.7 | .347/.437/.734/.478 | .52/.69/.94 | 40-60 worse (.48 vs .55); W Europe sky 78 (60-75, fails); PNW 86 |
| c. `sun_ref` 0.658 (the model's own 20-60 share, lane 126's untried) | unchanged | unchanged | warm month 20-40 +0.4 -> +0.2, 40-60 -0.1 -> -0.3; Köppen same |

**Recommendation: leave it.** No cloud candidate takes more than 0.03 off the 20-40 band without making the wet tropics
or the midlatitudes worse. Re-measure after the rain round, as the ticket already says. (c doesn't touch the sunshine.
It only re-centres the summer split on the model's own scale, and the summer temperatures don't need it now.)

## 4. PW-1335: the coldest month of warm semi-arid land

**What makes it.** `planet/climate.py::_winter_air`: on these cells the coldest month is the land's own winter,
`t_land - half_l` (`temp0` from `::temperature`, less `continental` x season strength + 0.3). The carried air adds
almost nothing (400-900 mm same cells: land-left-to-itself 13.5 C, carried 13.8, albedo -0.03, final 13.8, NCEP 16.4).
Clouds don't enter it (lane 125). The model's rain doesn't either: the miss regressed on ln(model rain / GPCC) over
warm land at 250-1500 mm has r = +0.28 and slope +0.53 C per e-fold (wetter model, slightly *warmer* winter). Where the
rain is within 30%, the miss is still -1.93 C.

**It grows with height** (all ice-free land, coldest-month miss C; mean-temperature and warmest-month misses go the same
way):

| abs(lat) | < 300 m | 300-700 | 700-1200 | 1200-2000 | > 2000 |
|---|---|---|---|---|---|
| 0-20 | -0.2 | -1.3 | -1.8 | -2.3 | -4.1 |
| 20-35 | -1.0 | -1.0 | -2.4 | -4.1 | -4.7 |
| 35-50 | +3.4 | +2.2 | +0.2 | -1.3 | -3.8 |
| 50-70 | -1.3 | -0.3 | -2.6 | -6.4 | -7.9 |

Regression on warm semi-arid land: coldest-month miss = -1.55 x height (km) + 0.65 x ln(rain ratio) - 1.89 x (winter
sunshine error) - 1.29. Mean temperature: -1.44 per km. `tools/earth_data.py` brings NCEP to each cell's own height
with 6.5 C/km from its pixel's mean height, so the model and the observation share the lapse rate. The slope is a real
"high ground is warmer than 6.5 C/km below the lowland says" signal (NCEP 2 m being a reanalysis field is the caveat).
That matches the mass elevation effect (He et al. 2016: ~5 K at 3700 m, i.e. ~1.35 C/km, from surface heating of the
raised ground; positive in winter too, more so at low latitude).

**The rest is not height.** Warm semi-arid low ground (< 300 m) with the rain within 30%: coldest month -1.63 C,
warmest month +0.94 C. The model's winter-to-summer range is ~2.6 C too large there. At 20-30 deg the range is 17.1 vs
13.9 observed; at 10-20 it is right (7.7 vs 8.1). The model gives dry sunny *summers* their sensible-heat warming
(`::_summer_split`). It gives dry sunny *winters* nothing: the winter is the curve less a fixed swing, whatever the
sky or the soil. That is my reading of the code, not a sourced claim. The sourced part is only the energy split itself
(FAO-56, lane 121/125). Not screened here.

**Candidates** (`mee_k` C per km of the ice-free ground's height smoothed over `mee_km`, capped at the cell's own
height, added to `temp0`; round2.patch):

| arm | Tc 400-900 same cells (NCEP 16.4) | cold month 0-20 / 20-40 / 40-60 | warm month 0-20 / 20-40 / 40-60 | S Africa sav / Mexico N / India dTc | Köppen A/B/C/D/E (Kottek 21.9/30.1/15.9/24.8/7.3) | exact / group, points | rain r |
|---|---|---|---|---|---|---|---|
| main | 13.8 | -1.1 / -1.6 / +1.0 | -1.6 / +0.4 / -0.1 | -2.6 / -6.2 / -3.8 | 20.3/24.5/19.4/24.2/11.7 | 36.6/70.7, 37/21/20 | 0.714 |
| a. 1.35 C/km, 300 km | 14.3 | -0.6 / **-0.6** / **+1.9** | -1.2 / +1.0 / +0.4 | -1.3 / -4.9 / -3.5 | 21.5/23.6/20.0/24.5/**10.4** | 35.7/70.7, 36/24/18 | 0.710 |
| b. 1.35 C/km, 600 km | 14.2 | -0.7 / -0.8 / +1.8 | -1.3 / +0.9 / +0.4 | -1.5 / -5.3 / -3.5 | 21.4/23.6/19.8/24.3/10.8 | 35.8/70.8, 36/23/19 | 0.710 |
| c. 0.8 C/km, 300 km | 14.0 | -0.8 / -1.0 / +1.5 | -1.4 / +0.7 / +0.2 | -1.8 / -5.5 / -3.6 | 21.0/23.9/19.7/24.3/11.1 | 36.3/70.9, 35/23/20 | 0.714 |

Side effects, plainly. All three warm every highland, so the 40-60 deg winters (already +1.0 C) get too mild. Köppen B
falls (24.5 -> 23.6, Kottek 30.1: the wrong way). Exact Köppen agreement drops 0.9 point (a). Land >= 35 C goes 0.9 ->
1.3% (NCEP 1.7, better). In the Congo, (a) makes the warmer plateau air rain more: 1735 -> 2596 mm (GPCC 1653) and sky
59.6 -> 69.8%. That passes the cloud range for the wrong reason. Not screened, and it must be before any merge:
the glaciers and ice caps (Tibet, the Andes, the Rockies warm 1-3 C), and the runs' ice ages through `temp0`.

**Recommendation:** none to merge. (a) is the sourced mechanism at the sourced size and fixes the 20-40 deg winters. But
it is only ~0.5 of the 2.6 C on the ticket's own cells, and it over-warms the midlatitude highland winters. Ticket it
as its own change, with the ice and 40-60 deg checks (draft). The bigger lowland part wants a winter energy split
first, cheap diagnosis before code (draft). Three strikes counted on this ticket (a, b, c).

## 5. Full Earth L7 table (one solve per arm)

| Earth L7 | main | floor30 | seastab300 | cu07 | sunref658 | mee135 | mee135w (600 km) | mee08 |
|---|---|---|---|---|---|---|---|---|
| shade 400-900/900-1500/>1500 (obs .27/.41/.53) | .31/.42/.54 | .33/.46/.58 | .31/.42/.54 | .33/.45/.58 | .31/.42/.54 | .32/.42/.54 | .31/.42/.54 | .31/.42/.54 |
| Tc 400-900 same cells (NCEP 16.4) | 13.8 | 13.8 | 13.8 | 13.8 | 13.8 | 14.3 | 14.2 | 14.0 |
| Tc 900-1500 same cells (NCEP 20.0) | 18.4 | 18.4 | 18.4 | 18.4 | 18.4 | 18.9 | 18.9 | 18.7 |
| MAT 400-900 same cells (NCEP 22.6) | 20.9 | 20.8 | 20.9 | 20.8 | 20.8 | 21.4 | 21.3 | 21.2 |
| summer sun 0-10 (CRU .462) | .395 | .351 | .395 | .347 | .395 | .389 | .389 | .391 |
| summer sun 10-20 (CRU .569) | .477 | .437 | .476 | .437 | .477 | .478 | .478 | .477 |
| summer sun 20-40 (CRU .669) | .758 | .732 | .757 | .734 | .758 | .742 | .745 | .748 |
| summer sun 40-60 (CRU .549) | .520 | .495 | .519 | .478 | .519 | .517 | .519 | .518 |
| warm month 0-20 (NCEP 26.5) | 24.8 (-1.6) | 24.7 (-1.8) | 24.8 (-1.6) | 24.7 (-1.8) | 24.7 (-1.8) | 25.2 (-1.2) | 25.2 (-1.3) | 25.1 (-1.4) |
| warm month 20-40 (25.6) | 26.0 (+0.4) | 25.9 (+0.3) | 26.0 (+0.4) | 25.9 (+0.2) | 25.9 (+0.2) | 26.6 (+1.0) | 26.5 (+0.9) | 26.4 (+0.7) |
| warm month 40-60 (18.5) | 18.3 (-0.1) | 18.2 (-0.2) | 18.3 (-0.1) | 18.2 (-0.3) | 18.2 (-0.3) | 18.9 (+0.4) | 18.8 (+0.4) | 18.7 (+0.2) |
| cold month 0-20 (NCEP 21.0) | 19.9 (-1.1) | 19.8 (-1.2) | 19.9 (-1.1) | 19.8 (-1.2) | 19.8 (-1.1) | 20.3 (-0.6) | 20.3 (-0.7) | 20.1 (-0.8) |
| cold month 20-40 (6.9) | 5.2 (-1.6) | 5.2 (-1.6) | 5.2 (-1.6) | 5.2 (-1.6) | 5.2 (-1.6) | 6.3 (-0.6) | 6.1 (-0.8) | 5.8 (-1.0) |
| cold month 40-60 (-11.9) | -10.8 (+1.0) | -10.8 (+1.0) | -10.8 (+1.0) | -10.8 (+1.0) | -10.8 (+1.0) | -10.0 (+1.9) | -10.1 (+1.8) | -10.3 (+1.5) |
| land >= 35 C (NCEP 1.7%) | 0.9 | 0.8 | 0.9 | 0.9 | 0.8 | 1.3 | 1.3 | 1.1 |
| India: dTw / dTc / summer sun (CRU) | -1.2 / -3.8 / .71 (.49) | -1.4 / -3.8 / .68 | -1.2 / -3.8 / .71 | -1.4 / -3.8 / .69 | -1.4 / -3.8 / .71 | -0.5 / -3.5 / .73 | -0.6 / -3.5 / .73 | -0.8 / -3.6 / .72 |
| Mexico N | -0.6 / -6.2 / .94 (.61) | -0.7 / -6.2 / .92 | -0.6 / -6.2 / .94 | -0.6 / -6.2 / .94 | -0.7 / -6.2 / .94 | +0.3 / -4.9 / .93 | +0.1 / -5.3 / .93 | -0.1 / -5.5 / .93 |
| Sahel | -3.9 / -2.4 / .46 (.63) | -4.1 / -2.4 / .42 | -3.9 / -2.4 / .46 | -4.2 / -2.4 / .42 | -4.1 / -2.4 / .46 | -3.1 / -2.0 / .48 | -3.1 / -2.1 / .48 | -3.4 / -2.2 / .47 |
| S Africa savanna | -3.0 / -2.6 / .42 (.58) | -3.2 / -2.6 / .38 | -3.0 / -2.6 / .42 | -3.3 / -2.6 / .37 | -3.2 / -2.6 / .42 | -2.4 / -1.3 / .40 | -2.5 / -1.5 / .40 | -2.7 / -1.8 / .41 |
| W Europe | -1.3 / -2.0 / .56 (.45) | -1.4 / -2.0 / .53 | -1.3 / -2.0 / .56 | -1.5 / -2.0 / .52 | -1.4 / -2.0 / .56 | -1.3 / -1.8 / .56 | -1.3 / -1.9 / .56 | -1.3 / -1.9 / .56 |
| sky % Amazon (65-80) | 80.9 | 82.6 | 80.9 | 83.9 | 80.9 | 81.9 | 81.9 | 81.5 |
| sky % Congo basin (70-80) | 59.6 | 63.0 | 59.6 | 61.3 | 59.7 | 69.8 | 68.9 | 65.6 |
| sky % W Europe (60-75) | 73.0 | 74.8 | 73.0 | 78.1 | 73.0 | 72.9 | 72.8 | 72.9 |
| sky % Siberia (60-70) | 64.8 | 65.6 | 64.8 | 68.1 | 64.8 | 63.5 | 63.8 | 64.2 |
| sky % Pacific NW (60-75) | 81.2 | 83.2 | 81.3 | 86.2 | 81.2 | 81.3 | 81.2 | 81.4 |
| sky % Australia interior (20-35) | 34.5 | 35.7 | 34.5 | 36.5 | 34.5 | 36.1 | 35.8 | 35.5 |
| Köppen A/B/C/D/E (Kottek 21.9/30.1/15.9/24.8/7.3) | 20.3/24.5/19.4/24.2/11.7 | 20.3/24.5/19.4/24.0/11.9 | 20.3/24.5/19.4/24.1/11.7 | 20.3/24.5/19.4/23.9/11.9 | 20.3/24.4/19.4/24.0/11.9 | 21.5/23.6/20.0/24.5/10.4 | 21.4/23.6/19.8/24.3/10.8 | 21.0/23.9/19.7/24.3/11.1 |
| BWh (Kottek 14.8) | 11.7 | 11.7 | 11.7 | 11.7 | 11.7 | 12.0 | 11.9 | 11.8 |
| Köppen exact / group % | 36.6 / 70.7 | 36.4 / 70.5 | 36.6 / 70.7 | 36.5 / 70.5 | 36.5 / 70.5 | 35.7 / 70.7 | 35.8 / 70.8 | 36.3 / 70.9 |
| log-rain r | 0.714 | 0.714 | 0.714 | 0.714 | 0.714 | 0.710 | 0.710 | 0.714 |
| points exact/group/miss | 37/21/20 | 37/21/20 | 37/21/20 | 36/22/20 | 37/21/20 | 36/24/18 | 36/23/19 | 35/23/20 |
| land sunshine RMSE vs CRU | 13.1 | 13.1 | 13.0 | 13.4 | 13.1 | 12.9 | 12.9 | 13.0 |

Main reproduces lane 126's final column (shade .31/.42/.54, 20-40 warm +0.4, >= 35 C 0.9%, Köppen 20.3/24.5/19.4/24.2/11.7,
r 0.714, Congo 59.6). The inland-deck arm (b of PW-1347) ran as a re-call only (no effect on any cloud number, so no
full solve).

## 6. Recommendations

| ticket | cause | recommended | strikes |
|---|---|---|---|
| PW-1347 Congo | no cool-season inversion off Gabon: the model's E equatorial Atlantic stays ~26 C (NCEP air 23.7 in its coldest month); no deck to carry inland | **leave it**; fix the sea first (draft), then re-try c (code in round2.patch) | 3 (floor, inland deck, sea stability) |
| PW-1348 summer sunshine | the rain: 70% of the excess is where the model's rain is < 0.6 x GPCC | **leave it**; re-measure after the rain round (as the ticket says) | 3 (floor, cumulus, sun_ref) |
| PW-1335 cool winters | ~1/3 height (mass elevation effect missing, -1.5 C/km), ~2/3 a dry-season winter warmth the model lacks | none to merge; ticket the mass elevation effect (a) with ice checks; diagnose a winter energy split | 3 (three mass-elevation arms) |

## 7. Drafts (issue-tracking/inbox)

- `draft-east-equatorial-atlantic-cold-season-too-warm.md`: the model's E equatorial / Gabon-Angola sea in its cool season
  (PW-1347's root).
- `draft-mass-elevation-effect-highland-temperature.md`: the -1.5 C/km height miss and candidate (a), with the checks it
  needs.
- `draft-winter-energy-split-dry-season-warmth.md`: lowland warm semi-arid winters 1.6 C cold, range 2.6 C too large;
  diagnose a winter counterpart of `_summer_split`.

## Files

screen2.py, winter2.py, ec2.sh, table2.py, round2.patch (this folder); reused withtune.py. Scratch outputs (under the
session scratchpad, l131/) deleted at the end; the downloaded papers were not kept. Inputs read: round1.md,
diagnosis.md, screen.py, planet/climate.py (`clouds`, `_layer_gate`, `_season_inputs`, `compute`, `_air_temps`,
`_winter_air`, `_summer_split`, `albedo_warming`, `temperature`, `seasons`), tools/earth_data.py (NCEP height
adjustment), tools/earth_check.py (CLOUD_REGIONS), PW-1347/1348/1335/1349.
