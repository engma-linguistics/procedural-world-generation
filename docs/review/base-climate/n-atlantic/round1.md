# Lane 142: the finished N Atlantic too warm (PW-1381), 2026-11-03

Status: **diagnosis done, Earth screens done, paired judge on arm l60 (moc_lambda 30 -> 60, commit a2815e10)
passes: section 4.**

Main = 0c1ca629. Everything here is Earth L6 unless it says L7. Scripts are in this directory:
- `get_sst.py`: how the observed SST was fetched;
- `seabox.py`: the model's sea against OISST by box;
- `heatcross.py`: the inflow's heat transport across latitudes;
- `ec.sh`: L7 earth_check plus L6 moisture_regions per arm;
- `summ.py`: the screen table;
- `launch.sh`: the judge.

## 0. How I judge the sea without an observed SST in the repo

The repo has no SST, and NCEP's 2 m air sits below the sea in winter, so I fetched one into scratch only (not
data/earth): NOAA OISST v2, 1 deg, 1991-2020 monthly long-term means (Reynolds et al. 2002; NOAA PSL
`downloads.psl.noaa.gov/Datasets/noaa.oisst.v2/sst.ltm.1991-2020.nc`, 3.4 MB, HDF5, read with `tools/h5_reader`).
`seabox.py` samples it at each cell's nearest pixel. It compares:
- the model's annual `sst` with OISST's 12-month mean;
- the model's warm and cold month (`sst_jul`, `sst_jan`) with OISST's warmest and coldest months;
- the model's air with NCEP.

## 1. Diagnosis: where the box's warmth comes from

Main, box 40-60 N, 60-10 W, split into quarters (SST and air in C):

| box | SST ann model / OISST | warm month | cold month | moc_heat | inflow share | winter half-swing own -> after winter_half | air ann model / NCEP | air cold month model / NCEP |
|---|---|---|---|---|---|---|---|---|
| N Atl storm track | 13.7 / 11.9 | 16.2 / 16.2 | 12.8 / 9.0 | +5.06 | 0.74 | 3.11 -> 0.89 | 14.3 / 10.7 | 12.3 / 6.6 |
| NW 50-60 N 60-35 W | 8.7 / 5.9 | 11.8 / 10.2 | 7.7 / 3.3 | +5.66 | 0.92 | 4.98 -> 0.99 | 8.7 / 4.2 | 5.6 / -1.4 |
| NE 50-60 N 35-10 W | 14.1 / 11.0 | 16.6 / 13.9 | 13.7 / 9.0 | +7.43 | 0.95 | 2.79 -> 0.39 | 15.1 / 10.0 | 13.5 / 7.4 |
| SW 40-50 N 60-35 W | 16.3 / 13.1 | 18.7 / 19.2 | 15.8 / 9.0 | +4.52 | 0.88 | 2.88 -> 0.52 | 17.2 / 11.7 | 15.7 / 6.2 |
| SE 40-50 N 35-10 W | 14.6 / 15.8 | 16.7 / 19.5 | 13.0 / 13.3 | +3.28 | 0.31 | 2.19 -> 1.55 | 15.0 / 15.0 | 13.3 / 12.1 |
| N Pac storm track | 8.7 / 8.5 | 11.1 / 14.0 | 6.2 / 4.9 | -0.50 | 0.14 | 3.11 -> 2.63 | 8.0 / 7.4 | 4.9 / 2.7 |
| Nordic seas 60-72 N, 20 W-15 E | 7.4 / 7.2 | 10.4 / 10.7 | 6.9 / 5.2 | +6.12 | 0.97 | 3.95 -> 0.51 | 7.7 / 5.3 | 5.2 / 2.1 |

The band means of the sea are right: OISST minus model is +0.5 at 40-50 N and +0.1 at 50-60 N. So `moc_zonal`'s
take-off is not too small in total. The error is *where* the inflow's warmth sits.

Splitting the box's cold-month air excess (+5.7 C against NCEP):
- **the annual SST, +1.8 C** (13.7 against 11.9; about +3 C in the NW, NE and SW quarters);
- **the winter swing cut by `winter_half`, ~+2 C.** The model's own winter half-swing is 3.1 C. `winter_half`
  cuts it to 0.9 under the inflow. OISST's is 2.9 (11.9 - 9.0).
- **the air over the winter sea, ~+1.9 C.** The model's winter air sits 0.5 C under its sea; NCEP's air sits 2.4 C
  under OISST (cold-air outbreaks).

Summer is right only by luck. The model's summer half-swing is 2.5 C against OISST's 4.3 (PW-593's one 50 m
layer), and that hides the +1.8 C annual excess.

**What drives the rain.** The rain follows the annual sea, not the winter swing:
- the w100 screen (section 2) fixes most of the winter swing and leaves the box's rain where it was;
- the box's summer evaporation is 1919 mm against NCEP's 610, with the summer SST right.

So (a), the swing, is a real error but not the rain's. **The rain's error is the annual +1.8 to +3 C of the
inflow's water over the subpolar gyre.**

**Why the inflow is too warm there: it gives up too little heat south of 55 N** (`heatcross.py`). The inflow's heat
transport above its sinking water (1.9 C, 12.5 Sv):

| latitude | 26.5 N | 35 N | 45 N | 55 N | 60 N | 65 N |
|---|---|---|---|---|---|---|
| main (moc_lambda 30): PW (inflow C) | 1.07 (22.9) | 1.04 | 0.91 (19.6) | 0.68 (15.3) | 0.61 (11.5) | 0.09 |
| moc_lambda 45 | 1.12 | 1.07 | 0.89 | 0.61 (13.0) | 0.49 | 0.04 |
| moc_lambda 60 | 1.13 | 1.07 | 0.85 | 0.54 (11.3) | 0.40 (7.1) | 0.02 |

Observed:
- **RAPID, 26.5 N: 1.33 PW** ("a mean MHT of 1.33 ± 0.40 PW for 10-day-averaged estimates"; annual-mean
  uncertainty 0.14 PW). Johns et al. 2011, J. Climate 24, 2429, read at nora.nerc.ac.uk/id/eprint/290085.
- **OSNAP, ~53-60 N: 0.45 PW** ("MHT across the entire OSNAP section yields a mean and uncertainty of 0.45 ± 0.02
  PW"). The overturning carries 73% of it. Lozier et al. 2019, Science 363, 516, full text read.
- They also say: "The heat transport divergence between these two lines, 0.80 PW, is the amount of heat stored or
  lost to the atmosphere as the warm Gulf Stream and North Atlantic Current waters…".

So:

| | of the 26.5 N heat, the share left at 60 N | lost on the way |
|---|---|---|
| Earth (0.45 / 1.33) | 34% | ~0.8 PW, over the Gulf Stream and North Atlantic Current |
| model, main | 57% | 0.46 PW |
| model, moc_lambda 60 | 35% | 0.74 PW |

The model's sinking (0.98 PW at the site) is not too strong. Its inflow keeps too much heat into the subpolar gyre
and loses it all at 55-65 N instead.

Other sources the helper read for context:
- Holte et al. 2017, GRL 44, 5618 (Argo MLD climatology): winter mixed layers "beyond 1500 m … in the Labrador
  and Nordic Seas", and "reaching 400 m … in the Gulf Stream". These are late-winter maxima.
- Jacobs et al. 2020, JGR Oceans (an ORCA12 hindcast, not observations): winter Qnet "exceeding 400 Wm-2" over
  the Gulf Stream path.
- Not found or not opened: a published SST annual range at 45-55 N. OISST itself gives it (above).

## 2. Candidates and Earth screens

- **(a) PW-593 / `winter_half`.** The cut takes the winter cooling as spread over the 500 m inflow layer
  (`moc_layer_m`). But the winter's cooling happens while the mixed layer deepens. The 400-1500 m depths are its
  late-winter maximum (Holte 2017).
  - OISST's winter half-swing under the inflow is ~2-2.6 C: NE 2.0, Nordic 2.0, NW 2.6. That is about half the
    open-ocean ratio (N Pacific 3.6 against own 3.1).
  - Screened as a separate depth `moc_winter_m`: 100 m gives Nordic 2.04 (OISST 2.0), NW 2.74 (2.6), NE 1.46 (2.0).
  - It moves the box's cold month 12.8 -> 12.1 (OISST 9.0) and the air's cold month 12.3 -> 11.4.
  - It doesn't move the rain (winter P 2765 -> 2715), and it raises the sinking 12.5 -> 13.6 Sv.
  - The 100 m is fitted to OISST's swing; no source states a cooling-season mean depth.
  - **Not taken here. Draft for PW-593.**
- **(b) The inflow's heat loss along its route, `moc_lambda`.** The rate at which it gives its heat to the air
  over it.
  - Set by RAPID -> OSNAP: 60 W/m2 per C leaves 35% of the 26.5 N heat at 60 N, against Earth's 34%.
  - It is planet-generic: one exchange rate. It is fitted to the process's own observed budget, not to the box's
    temperature.
  - **Chosen.**
- **(c) Relax the inflow toward the air over it instead of the latitude's sea** (cold continental air over the
  Gulf Stream).
  - Screened with pass 1's air as the target, using a temporary switch that has since been removed.
  - The box changed by only -0.4 C, and the heat left at 55 N *rose* to 1.27 PW, because the subtropical gyre's
    air is warmer than t_eq.
  - **Rejected.**
- **`moc_zonal`:** not the cause; the band means are right (section 1).
- **The air's winter fetch over open water (`air_km_sea` 300 -> 600 / 1000).**
  - Lowers the box's winter air by 0.7 / 2.0 C.
  - But it overshoots the Nordic seas' winter air (5.2 -> 3.0 / 0.3 against NCEP 2.1).
  - **Draft only.**

**Earth screens** (L7 earth_check; L6 moisture_regions --no-cf; same code, only the tune differs):

| | main | w100 | l45 | l60 | l60 + w100 |
|---|---|---|---|---|---|
| B % (Kottek 30.1) | 25.40 | 25.37 | 25.26 | 25.14 | 25.13 |
| exact / group % | 36.3 / 70.6 | 36.2 / 70.6 | 36.3 / 70.6 | 36.4 / 70.6 | 36.3 / 70.7 |
| log-rain r | 0.713 | 0.71 | 0.71 | 0.71 | 0.71 |
| land P (GPCC 791) | 1030 | 1030 | 1036 | 1040 | 1040 |
| global T (NCEP 14.0) | 13.89 | 13.83 | 13.87 | 13.86 | 13.81 |
| land P 90-80 / 80-70 / 70-60 S | 94.9 / 174 / 316 | 96.1 / 174 / 316 | 96.0 / 177 / 320 | 96.9 / 179 / 323 | 98.0 / 180 / 323 |
| Greenland P | 407 | 408 | 398 | 389 | 386 |
| sea P 40-50 / 50-60 / 60-70 N (GPCP 1300 / 1148 / 905) | 1318 / 1480 / 778 | 1309 / 1491 / 763 | 1279 / 1344 / 675 | 1248 / 1250 / 610 | 1234 / 1246 / 601 |
| N Atl box Oct-Mar P / E (GPCP 1651 / NCEP 1339) | 2765 / 1991 | 2715 / 1949 | 2476 / 1691 | 2265 / 1473 | 2207 / 1421 |
| N Atl box Apr-Sep P / E (1057 / 610) | 1760 / 1919 | 1849 / 2014 | 1510 / 1650 | 1338 / 1463 | 1396 / 1526 |
| N Pac box Oct-Mar P / E (1465 / 882) | 1096 / 319 | 1078 / 308 | 1108 / 325 | 1121 / 334 | 1111 / 329 |
| W Europe P (903) | 1107 | 1099 | 1128 | 1142 | 1134 |

The SST against OISST and the air against NCEP (`seabox.py`; ann / cold month, C):

| | main | l60 | OISST / NCEP |
|---|---|---|---|
| box SST | 13.7 / 12.8 | 11.9 / 11.0 | 11.9 / 9.0 |
| box air | 14.3 / 12.3 | 12.4 / 10.5 | 10.7 / 6.6 |
| NE quarter SST | 14.1 / 13.7 | 11.3 / 10.9 | 11.0 / 9.0 |
| NW quarter SST | 8.7 / 7.7 | 6.2 / 5.2 | 5.9 / 3.3 |
| Nordic seas SST | 7.4 / 6.9 | 4.5 / 4.0 | 7.2 / 5.2 |
| sea 50-60 N / 60-70 N band SST | 7.22 / 3.50 | 6.46 / 2.09 | 7.12 / 4.30 |

**Reading l60:**
- **The box:**
  - annual SST right (11.9 against 11.9);
  - winter evaporation 1.10x NCEP (was 1.49x), inside the ticket's 0.7-1.3x;
  - winter rain 1.37x GPCP (was 1.67x);
  - the 50-60 N sea rain 1250 against 1148 (was 1480).
- **The snow comes back to the far south.** Antarctic land rain is +2.1% / +2.9% / +2.2% by band. The rest of the
  globe pays less for the box (section 5 of lane 134's round 2).
- **The land is unchanged or slightly better:** B -0.3 points, log r and Köppen unchanged, global T -0.03.
- **What gets worse is downstream of 60 N:**
  - the Nordic seas 2.7 C cooler than OISST (they were right);
  - the 60-70 N sea band 2.2 C cool (was 0.8) and its rain 610 against GPCP 905 (was 778);
  - Greenland's snow -4.4%.
  - Main sends 0.61 PW past 60 N, against OSNAP's 0.45. Behind its right Nordic seas sit a box 3 C too warm and
    the inflow's release crammed into 55-65 N. l60 sends 0.40 PW past 60 N but releases it all by 65 N, so the
    Norwegian Sea's own inflow (the route east of Iceland) is short.
  - **Draft:** the inflow's route north of 60 N (sinking at 68 N, 33 W, the East Greenland side, not the Nordic
    seas' interior).
- **The box's winter air** is still 3.9 C over NCEP in the cold month. The rest is the swing (a) and the
  cold-air outbreak gap. So the ticket's "winter-half sea air within ~2 C" is not met by l60 alone.

l45 is the half-way point: 44% of the heat left at 60 N, box winter E 1.26x, Nordic -1.6 C. The source points to
60, so l60 went to the judge.

## 3. Short L6 draws

Skipped. The paired judge has the cold-edge and warm-edge draws (l6c_m / l6c_p) and only ran once (section 4).

## 4. Paired judge (2 rolls, 36 draws per arm; main 0c1ca629, cand a2815e10)

Ran 00:18-05:47, 2026-11-03 (`launch.sh 0.0005 0.001`, MAXSIM 4 x THREADS 3). Read with
`pjudge.py $S/judge main cand --table` and `tools/hard_bar.py` per arm (symlink folders, removed after).

**It passes the bar.**
- **Hard failures: 0 on both arms.** Frozen over, boiled, ocean loss and CO2 crash are all 0/36.
- **Soft passes:** main 30/36 (14/18 + 16/18), cand 28/36 (15/18 + 13/18). Both pass 22 draws, main only 8, cand
  only 6. McNemar p 0.79, so within chance; lane 24's null change moves 7-8 draws.
- **Late dT:** main median 1.77, cand 1.05; paired B-A -0.12 [-1.58, +0.64], 17 / 19, not moved. Inside
  HUMAN_RANGE (-6..+5).
- **Glacial maxima:** main 13, cand 17 (lane 134's merge had taken them 23 -> 13).
- **Moved:** only the source reference, +0.05 [+0.01, +0.07] (sign p 0.065).
- **Not moved:**
  - end T -1.5 [-3.2, +1.0];
  - late CO2 +0.01;
  - land rain -6 [-36, +12];
  - arid +0.8, hot desert -0.2, trees -1.1.
- **Reported, not on the bar:** draws whose end pCO2 lies outside 180-600 ppm went from 11 to 19. Draws under
  100 ppm went from 2 to 1.

**Reading:**
- This takes back most of PW-1364's warming: the late dT that PW-1364 raised by +0.57 C now moves by -0.12 against
  the same worlds on main, and glacial maxima recover 13 -> 17.
- That fits the mechanism: the over-wet N Atlantic took snow from the ice sheets, and Antarctic land rain is +2-3%
  on Earth.

## 5. Not yet done

- the full test suite and the golden update (the outputs change on purpose);
- `tools/scorecard.py` and `tools/earth_check.py` on the candidate.
