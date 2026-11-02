# Lane 126: tropical cloud and the summer split, round 1 (PW-1334, PW-1327, PW-1336, with PW-1326's B+C), 2026-11-02

Status: **code done, Earth screens done; L6 sanity and the paired judge below.** Base: main e89de6af (merged).
Harness (this folder): [screen.py](screen.py) (Earth L7 bands, cloud regions, warm month, lake evaporation; `--recall`
re-calls `climate.clouds` on the solved inputs with other knobs, no re-solve), [ec.sh](ec.sh) / [batch.sh](batch.sh)
(screen.py + tools/earth_check.py per arm, TUNE overrides through [withtune.py](withtune.py)). Earth runs read a private
copy of data/earth in the worktree (data/earth itself was only read). Scratch outputs are deleted at the end.

## In plain words

- **The tropics' extra cloud was a winter-stratus rule firing in warm air.** The land's humidity-layer cloud
  (`cloud_rh` x humidity^1.5) now needs stable air: air aloft as warm as, or warmer than, the ground's. Over
  winter Europe, Siberia and Canada it stays as before; over tropical land and summer continents it thins or goes.
  The Earth model's warm-land shade is now 0.31 / 0.42 / 0.54 at 400-900 / 900-1500 / >1500 mm against observed
  0.27 / 0.41 / 0.53 (was 0.40 / 0.55 / 0.69). W Europe's cloud now passes inside its range (73%, was 79%).
- **The summer heating now reads sunshine, not sky cover,** and its reference is CRU's summer sunshine of Earth's
  20-60 deg land (0.62). On top, lane 121's two sourced changes (clear skies lose more long-wave; a hot dry ground
  mixes a deeper layer). Earth's subtropical summer excess goes from +2.1 C to +0.4 C, and land with a warmest month
  of 35 C or more from 7.9% to 0.9% (observed 1.7%).
- **Lakes and the cell inspector now read the light's cloud too.** Lake Victoria evaporates 1635 mm/yr (observed
  ~1500, PW-358's docstring), the Amazon floodplain 1661.
- **Costs.** The Congo basin's cloud falls below its range (60% vs 70-80; its sunshine 0.57 vs CRU 0.45). Summer
  subtropical land gets too sunny (20-40 deg summer sunshine 0.76 vs CRU 0.67; worst where the model's rain is
  already too low: India, N Mexico). The wet tropics' summers stay 1.6 C cool (rain too high in the Sahel and W
  Africa, so evaporation takes the heat). Arabia (-2.5 C) and the US Southwest (-5.2 C, cold already) cool, and
  Köppen B goes 25.0% -> 24.5% (Kottek 30.1): lane 121's known costs. Drafts for each.

## 1. Sources: what gates low stratiform cloud over land (PW-1334 step 1)

Read in this lane:

- **Klein & Hartmann 1993**, "The seasonal cycle of low stratiform clouds", J. Climate 6:1587. Abstract read on NASA
  NTRS (19930071203; the AMS PDF was blocked): "Ten regions of active stratocumulus convection are identified. These
  regions fall into four categories: subtropical marine, midlatitude marine, Arctic stratus, and Chinese stratus.
  With the exception of the Chinese region, all the regions with high amounts of stratus clouds are over the
  oceans. In all regions except the Arctic, the season of maximum stratus corresponds to the season of greatest
  lower-troposphere static stability. ... a 6 percent increase in stratus fractional area coverage is associated
  with each 1 C increase in static stability." (Their stability: theta at 700 hPa less theta at the surface, per
  the citing literature; I did not read the body.)
- **Eastman & Warren 2014**, "Diurnal cycles of cumulus, cumulonimbus, stratus, stratocumulus, and fog from surface
  observations over land and ocean", J. Climate 27:2386 (PDF from atmos.uw.edu/~rmeast, read): "Much stronger
  seasonal shifts are seen over land ... Diurnal cycles over North America and Europe are small or dominated by St
  and Sc in winter, but by Cb and especially Cu during summer." And the mechanism: "During daytime clouds form due
  to the destabilization of the boundary layer by solar heating of the surface, driving convection and generating
  cumuliform clouds. At night the boundary layer cools, eventually causing condensation to form stratiform clouds."
- **Cermak et al. 2009**, "European climatology of fog and low stratus based on geostationary satellite
  observations", QJRMS 135:2125 (read, abstract and intro): the climatology is built from winter seasons, where fog
  and low stratus are the European phenomenon of interest. Supports winter, not summer, as Europe's stratus season.

Not found / not read: a tropical-land low-cloud climatology (ISCCP / CloudSat by cloud type over savanna). Warren
et al. 1986's land atlas (NCAR TN-273) is a scanned PDF I could not text-search. Wood & Bretherton 2006 (EIS) did not
download. So the claim "savanna cloud is mostly convective" is still not directly sourced; what is sourced is the
control: **lower-tropospheric stability**, with land stratus a winter (stable) cloud and summer land cloud cumuliform.

**Which control in the model.** Three candidates measured on Earth L7 (`screen.py --prox`), by half-year:

| region, half-year | lts = t_ref - (t_air + height), C | -inst (moist), C | t_sl, C | rh |
|---|---|---|---|---|
| warm land 400-900 mm, Jul / Jan | -0.7 / -1.7 | 11.7 / 7.8 | 24.7 / 25.8 | 0.63 / 0.67 |
| warm land >1500 mm, Jul / Jan | -0.8 / -1.0 | 4.0 / 3.0 | 26.6 / 26.8 | 0.79 / 0.78 |
| W Europe, Jul / Jan | -5.7 / 2.0 | -2.2 / 0.0 | 15.5 / 4.2 | 0.55 / 1.00 |
| Pacific NW, Jul / Jan | -5.4 / -0.3 | -3.8 / -2.9 | 15.4 / 6.8 | 0.74 / 1.00 |
| Siberia, Jul / Jan | -8.5 / 14.9 | -5.9 / 19.5 | 10.7 / -15.4 | 0.43 / 0.82 |
| Canada, Jul / Jan | -8.5 / 11.6 | -6.2 / 15.2 | 13.5 / -10.0 | 0.48 / 0.91 |

`t_ref` (`_season_inputs`) is the model's air aloft in surface-equivalent terms (the warmest sea in the tropics,
the latitude's sea poleward), so `t_ref - (t_air + height)` is the model's lower-tropospheric stability with the
moist-adiabatic part taken out (an EIS-like measure): ~0 over tropical land, negative over summer continents,
positive over winter continents. That matches Klein & Hartmann's control and Eastman & Warren's winter-St / summer-Cu
split. The moist index (-inst) calls dry savanna *stable* (it is dry, not stable) and was dropped. Temperature (t_sl)
separates the tropics best but is a correlate, not the control; it was screened as a comparison (below).

## 2. A: the stability gate (`climate.py::_layer_gate`, `cloud_rh_lts`)

`cloud_rh x rh^1.5 x clip((lts + a) / b, 0, 1)`. Sweep by re-calling clouds on the solved Earth inputs (no re-solve;
shade same cells, summer sunshine by band, annual sky %, summer sunshine of regions):

| arm | shade 400-900/900-1500/>1500 (obs .27/.41/.53) | summer sun 0-10 / 10-20 / 20-40 / 40-60 (CRU .46 .57 .67 .55) | sky % W Eur / PNW / Siberia / Amazon / Congo (60-75, -, 60-70, 65-80, 70-80) | summer sun W Eur / PNW / India / Mex N / SE USA (CRU .45 .62 .49 .61 .64) |
|---|---|---|---|---|
| main | .40/.55/.69 | .25 .34 .67 .44 | 79 88 68 87 71 | .45 .33 .61 .87 .54 |
| **lts 2:6 (chosen)** | **.31/.42/.54** | .40 .48 .76 .52 | 73 81 65 81 60 | .56 .48 .71 .94 .66 |
| lts 2:6, floor 0.3 | .33/.46/.58 | .35 .44 .73 .50 | 75 83 66 83 63 | .53 .43 .68 .92 .62 |
| lts 4:8 | .32/.44/.57 | .40 .48 .76 .52 | 74 82 65 82 62 | .56 .48 .71 .94 .66 |
| temperature 30:20 (comparison) | .29/.40/.53 | .39 .47 .75 .47 | 78 86 67 80 60 | .48 .37 .71 .93 .63 |
| no cloud_rh at all | .24/.36/.50 | .40 .48 .76 .52 | 69 80 52 78 59 | .57 .48 .71 .94 .66 |

- lts 2:6 brings all three bands within 0.04 of observed, and W Europe / Siberia stay in range (Siberia keeps its
  winter stratus: gate 1 at lts +15). It is the sourced control and better on the 40-60 deg summer sunshine than the
  temperature gate; the temperature gate keeps W Europe's summer sunshine right but leaves W Europe 78% and the
  Pacific NW as dark as main. A floor (keep 30% of the layer in unstable air) keeps the summer midlatitudes nearer CRU
  but leaves the bands 0.05-0.06 off. Chosen: lts 2:6, no floor.
- Every gate pushes the 20-40 deg summer sunshine past CRU (.67 -> .73-.76). Where: India .71 vs .49 and N Mexico
  .94 vs .61, both already too sunny on main, where the model's rain is too low (PW-1326 / lane 121's table: India
  627 mm vs GPCC 1126, N Mexico 199 vs 482). So it is the rain's deficit showing through, not the gate. Draft.

Full solve (A alone, earth_check; then the rest):

| Earth L7 | main | A | A+B (sun_ref .62) | A+B + lw | A+B + deep layer | **A+B + lw + deep layer (+C)** |
|---|---|---|---|---|---|---|
| shade 400-900 / 900-1500 / >1500 (obs .27/.41/.53) | .40/.55/.69 | .31/.42/.54 | same | same | same | .31/.42/.54 |
| warmest month 0-20 deg (NCEP 26.5) | 24.6 (-1.9) | 24.9 (-1.5) | 24.7 (-1.8) | 24.9 (-1.5) | 24.6 (-1.9) | 24.8 (-1.6) |
| 20-40 deg (25.6) | 27.7 (+2.1) | 28.2 (+2.6) | 27.1 (+1.4) | 26.5 (+0.9) | 26.3 (+0.6) | **26.0 (+0.4)** |
| 40-60 deg (18.5) | 18.3 (-0.2) | 18.7 (+0.2) | 18.1 (-0.4) | 18.4 (-0.1) | 18.0 (-0.5) | 18.3 (-0.1) |
| land >= 30 C (NCEP 16.1%) | 17.8 | 18.9 | 17.0 | 16.1 | 15.3 | 14.7 |
| land >= 35 C (NCEP 1.7%) | 7.9 | 8.6 | 5.7 | 3.2 | 1.5 | **0.9** |
| Sahara (31.5) | +4.7 | +5.1 | +3.3 | +2.1 | +1.4 | +0.8 |
| Arabia (33.9) | +0.8 | +1.4 | -0.3 | -1.3 | -2.0 | -2.5 |
| India (32.6) | +0.7 | +1.3 | +0.1 | -0.4 | -1.0 | -1.2 |
| US Southwest (26.1) | -3.5 | -2.8 | -4.2 | -4.9 | -4.8 | -5.2 |
| Mexico N / SE USA | +2.7 / +4.4 | +3.3 / +4.9 | +1.3 / +4.2 | +0.2 / +4.1 | +0.1 / +3.9 | -0.6 / +3.8 |
| Sahel / W Africa coast | -3.9 / -3.3 | -3.5 / -3.1 | -3.8 / -3.2 | -3.6 / -2.8 | -4.2 / -3.2 | -3.9 / -2.8 |
| Pacific NW / W Europe / Siberia | -5.4 / -1.4 / -0.8 | -5.1 / -1.0 / -0.4 | -5.3 / -1.5 / -1.1 | -5.1 / -1.3 / -0.6 | -5.3 / -1.5 / -1.1 | -5.1 / -1.3 / -0.6 |
| Köppen A / B / C / D / E % (excl. Ant.) | 20.1/25.0/19.2/23.9/11.8 | 20.2/25.3/19.0/24.6/10.9 | 20.2/24.8/19.2/23.6/12.2 | | | 20.3/24.5/19.4/24.2/11.7 |
| BWh % (Kottek 14.8) | 12.9 | 13.1 | 12.5 | | | 11.7 |
| Köppen exact / group % | 37.2 / 70.4 | 37.3 / 70.9 | 37.1 / 70.3 | | | 36.6 / 70.7 |
| log-rain r | 0.714 | 0.714 | 0.714 | | | 0.714 |
| point check exact / group / miss | 37/21/20 | 38/20/20 | 37/21/20 | | | 37/21/20 |
| land sunshine RMSE vs CRU (points) | 15.3 | 13.1 | 13.1 | | | 13.1 |
| land cloud regions failing | Amazon (86.6) | Congo (59.7) | Congo | | | Congo (59.6) |

(Trade cumulus (Hawaii) fails on every arm, a sea region the change doesn't touch. Blank cells: earth_check not run on
that arm; screen.py rows only.)

## 3. B: the split reads sunshine (`_summer_split`, `sun_ref`)

- The split now takes `clouds()`' sunshine share (convective cloud at `cloud_sun_conv`) in place of
  `sunshine(sky cover)`, and its reference is `sun_ref` = 0.62, CRU's summer sunshine share on Earth's ice-free land
  20-60 deg (measured here: 0.618; PW-1327's 0.62). The model's own share there after A is 0.658; I kept CRU's
  number, as the ticket asks (both are on the same scale now; using 0.658 would cool 20-60 deg by ~0.3 C more).
- The reference move matters as lane 121 said: reading sunshine with the old reference (0.383) gives 0-20 deg -0.3
  but 20-40 +3.2 and 40-60 +1.3; with 0.62, 0-20 -1.8, 20-40 +1.4, 40-60 -0.4.
- **The wet tropics stay ~1.6 C cool after all of it.** Their summer sunshine is now 0.40 / 0.48 (0-10 / 10-20 deg)
  against CRU 0.46 / 0.57, and their evaporation is the model's rain's: Sahel 2094 mm vs GPCC 596 in lane 121's table.
  That is the rain (PW-228's regional rain, PW-rain-inland), not the split's reading. Not chased further.
- Then lane 121's B (`split_lw` 1, FAO-56 eq. 39) and C (`split_bl_max` 4, Ryder et al. 2015) on top, now on by
  default; code as in [../summer-heat/candidates.patch](../summer-heat/candidates.patch) with the reference on the
  sunshine scale. Both moved the warm months the intended way on the new reference (table above).

## 4. C: lakes and the inspector read the light's cloud (PW-1336)

`climate.compute` and `planet/nest.py` pass `shade(sun_*)` / `out["shade_*"]` to `open_water_evap`; the server's
`/api/cell` builds the shade from the world's `sunshine_jul/jan` layers (`climate.shade_from_hours`), as the plants
see it (world.py). FAO-56 ch. 3's Angstrom-Prescott relation is in relative sunshine duration (lane 125 read it).

| lake evaporation, mm/yr (A+B+C) | shade (now) | sky cover (old reading) |
|---|---|---|
| Lake Victoria | 1635 | 1357 |
| Amazon floodplain | 1661 | 1379 |
| Lake Chad | 2147 | 1967 |
| Caspian | 1328 | 1323 |
| Great Basin | 772 | 709 |
| Lake Eyre | 2081 | 1931 |

Lake Victoria's observed ~1500 (open_water_evap's docstring, PW-358). Earth's closed basins with the model's rain:
unchanged (Caspian closed 73, Great Basin 12, Lake Eyre 12, Chad 21, Balkhash 23 vs 25, Tarim 8, Okavango 15, Altiplano
7). With GPCC rain the Caspian flips closed <-> open between arms (main closed, A open, A+B closed, A+B+lw+bl closed,
+C open), with lake evaporation there unchanged (1328 vs 1323): a knife-edge basin, not this change. Draft.

## 5. L6 sanity and the paired judge

Code frozen per arm (main = e89de6af by `git archive`; cand = this branch's planet/ and tools/ at 3637d117), run
through `../v1-finish-16/paired.sh` (L6, 1 Gyr, `tools/ice_diag.py`, star_brightening 1), judged with `pjudge.py`.

**Sanity: the 4 l6fix seeds, roll 0.0005** (seeds 957317, 619496, 583167, 639472):

| seed | main: pass, end T, arid %, land %, late CO2 | cand |
|---|---|---|
| 583167 | PASS +3.3, 20.2, 33.4, +0.04 | PASS +0.4, 18.7, 34.5, +0.44 |
| 619496 | PASS +2.9, 26.4, 35.1, +0.75 | PASS +4.7, 21.9, 35.1, +0.64 |
| 639472 | PASS +2.0, 24.7, 34.2, +0.63 | PASS -3.9, 21.2, 33.6, +0.34 |
| 957317 | PASS -5.4, 23.5, 35.3, +0.19 | PASS -0.2, 19.4, 34.1, +0.17 |

Paired medians (B - A, 95% interval): late dT -0.37 [-2.07, +2.13], late CO2 -0.06 [-0.29, +0.40], sink ref +0.03,
land -0.3: not moved. Arid % -3.8 [-4.5, -1.5], hot desert -2.9 [-4.9, -0.5], land rain +37 mm [+22, +77],
trees +4.4 points [+0.5, +9.3]: moved, all four draws the same way. 4/4 pass on both. So no systematic dT drift
(lane 121's -1.5 / -6.8 on two un-rolled seeds isn't there on re-rolled draws); the climate gets less arid and more
wooded. That's expected from the mechanism: cooler dry summers (deep layer, long-wave) lower the PET, and the
tropics' sunnier, warmer wet seasons don't raise it as much. Note: Earth's Köppen B moved the same way (25.0 ->
24.5 vs Kottek 30.1), and PW-290 has L7 worlds too arid (38-42%). Which way that nets depends on the level.

**Paired judge, 2 rolls (36 draws per arm): RUNNING at hand-off (lane 126 handed off at its context limit).**

- Launched 06:36 on 2026-11-02, both arms into one out root, MAXSIM 10 shared, detached (nohup):
  `paired.sh <S>/code/main <S>/judge main 0.0005 0.001` and the same for `<S>/code/cand ... cand`, with
  S = /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l126.
  Launcher logs `<S>/launch_main2.log` and `<S>/launch_cand2.log` end with "all done". The 8 sanity draws (l6fix r0.0005)
  are reused. Expect ~1.5-2 h at 10 at once (~15 min per run).
- To finish: once both logs say "all done", `ls <S>/judge/*/seed*.json.gz | wc -l` should be 72. A draw that died has a log
  but no seed*.json.gz: delete that log and re-launch the same paired.sh line. Then
  `uv run python docs/review/base-climate/v1-finish-16/pjudge.py <S>/judge main cand --table` and paste the tables here.
- **Bar:** hard failures 0 (frozen over, hellhouse); soft pass ~main's or better (sanity 4/4 vs 4/4); late dT / CO2 / sink
  ref not moved, or moved by what the mechanism explains; arid % / BWh down and trees up are expected (sanity).
- **Don't delete `<S>` until the judge is read**: the frozen code copies and the draws live there. After that, delete
  `<S>` (no symlinks inside it; `rm -rf "${S:?}"`). The worktree's private `data/earth/` copy (51 MB, gitignored) can go too.

## 6. State at hand-off, and what's next

- **Done:** sources (section 1); A, B, C coded and committed (3637d117 + this note), with lane 121's lw + deep layer on by
  default; Earth L7 screens (section 2 tables); lake measures (section 4); `pytest -m "not slow"` passes except the two
  goldens, which were updated for this change (sky -> sunshine and the gate move every climate output);
  `tests/test_envelopes.py` (slow) 11 passed; L6 sanity (section 5).
- **Running:** the paired judge (section 5).
- **Next:** read the judge and report to the coordinator before any merge. If it passes, say so plainly; PW-1334, PW-1327,
  PW-1336 and PW-1326 (B+C) close together on merge. Run `tools/scorecard.py` at merge (CLAUDE.md, after model changes).
- **Strikes:** none. A, B and C each moved its target the right way on the first try.
- **Open candidates, not tried:** a floor on the gate (30% keeps the summer midlatitudes nearer CRU, but the tropical
  bands land 0.05-0.06 off); sun_ref at the model's own 20-60 deg share (0.658, ~0.3 C cooler at 20-60 deg); C alone
  without lw (closest on the >= 35 C tail, 1.5%). None is needed for the tickets' bars.
- **Drafts (issue-tracking/inbox):** draft-congo-low-cloud-under-stability-gate, draft-subtropical-summer-too-sunny-after-cloud-gate,
  draft-caspian-closed-open-knife-edge, draft-wet-tropics-summer-cool-from-rain.

## Files

screen.py, ec.sh, batch.sh, withtune.py (this folder). Code: planet/climate.py (`clouds`, `_layer_gate`,
`_summer_split`, `_sum_air`, `compute`, TUNE `cloud_rh_lts`, `sun_ref`, `split_lw`, `split_bl_max`),
planet/nest.py, planet/server.py, tests/test_server.py, goldens.
