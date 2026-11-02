# PW-950 round 3 addendum (lane 100d): where the land goes, why the world cools, and the early shelf collapse

Written from cheap screens. A 36-draw judge of `slope_k=300` alone was started and stopped at 29 of 36 paired draws
when the owner narrowed the lane to proposals only (no judge, no fixes). Part 5 gives those 29 draws as supporting
evidence, not as a judge.
Harness: [tracediag.py](tracediag.py) (margindiag.py plus, every step, land, sea level and its parts, the CO2 source
and sink against their references, the weathering supply, the creep's net transfer from continental to oceanic crust
and the shelf; every 10 Myr, and every step over 80-200 Myr, the continental crust's hypsometry, its cover, the
oceanic crust's cover and the water it displaces, the continental crust budget by process (`sim.budget`) and the
continental crust born from sediment piles). Code: the branch at `28e93828` (main `1cd07bf4` merged), frozen copies.
L6, 1 Gyr, default settings, seeds 1 and 3; late = the 600-1000 Myr mean.

## In plain words

The creep doesn't drown land by raising the sea. In the creep runs the sea actually stands lower (the world is
colder, so there is more ice). The land goes because more of the continental crust ends up deep under water. The
creep strips the sediment off the drowned edges of the continents and carries it out onto the ocean floor. There it
piles up into a rise, and once a pile is 13 km thick the model counts it as new continent, a deep and drowned one.
The continents' total area is held fixed by a thermostat, so drowned rises use up area that would otherwise be land.

The cooling comes the same way, through another thermostat, not from the loss of land. Less land on its own would
warm the world: it weathers less, so CO2 goes up. But the model holds the continents' total volume steady by growing
volcanic arcs, and arcs breathe out CO2. Early in the run the creep moves continental sediment out to sea quickly. The
volume thermostat answers with about 20% more arc growth, and the CO2 source's reference is learnt during those years
(the first 300 Myr). Later the drowned rises turn into continent and make up the volume instead, so the arcs grow
less. The source then sits below the reference it learnt, CO2 falls and the world cools. A sediment process ends up
setting the volcanic CO2. That coupling is the thing I'd fix.

The early shelf collapse (5% at 100 Myr, 1.3% at 150 Myr) isn't a margin process. At 100 Myr the sea stands about
235 m high, from the start-up's young ocean floor, and the "shelf" is the flooded low plain of the start-up
continents. Between 100 and 150 Myr the continents come together in every one of the 36 draws (continental area -2.9
points, mean continental crust +2.2 km). The collision squeezes and lifts the flooded plains, and in half the draws
the sea falls 100 m or more as well.

## 1. Where the land goes (seed 1 / seed 3, late means)

| | main (k0) | slope_k 300 | slope_k 1000 |
|---|---|---|---|
| land % | 35.0 / 35.0 | 33.0 / 33.8 | 32.9 / 31.9 |
| continental crust % of the surface | 41.4 / 41.2 | 41.1 / 40.9 | 42.1 / 41.8 |
| sea level (m, with ice) | -15 / +24 | -53 / -16 | -226 / -116 |
| ... continents' water part `sea_cont` | -21 / -11 | -34 / -10 | -45 / -54 |
| continental crust by elevation, % of it: > 500 m | 39.9 / 42.7 | 47.1 / 44.4 | 49.2 / 45.2 |
| ... 0-500 m | 43.5 / 41.8 | 30.9 / 37.8 | 26.8 / 28.5 |
| ... -400..0 m | 5.4 / 4.7 | 6.7 / 5.4 | 8.0 / 7.8 |
| ... below -400 m | 11.2 / 10.8 | 15.3 / 12.4 | 16.0 / 18.5 |
| cover on submerged continental crust (km) | 5.9 / 6.1 | 5.4 / 6.5 | 4.7 / 4.4 |
| mean cover on oceanic crust (km) | 0.42 / 0.44 | 0.61 / 0.60 | 0.71 / 0.62 |
| creep's net move, continental to oceanic crust, 0-1000 Myr (km x L5 cells) | 0 | 12 300 / 12 400 | 23 600 / 22 600 |

Seed 1 also with the continental crust budget and the sediment-born continent (rerun with the extra fields;
land 35.0 against 33.1):

| seed 1, km x L5 cells | main 0-300 / 300-600 / 600-1000 | slope_k 1000 |
|---|---|---|
| erosion (+ creep) | -12 054 / -13 597 / -18 284 | -17 465 / -26 080 / -36 317 |
| born (ocean crust piled to 20 km becomes continental) | 5 592 / 7 934 / 12 386 | 9 618 / 24 716 / 44 214 |
| coherence (thin isolated continental cells shredded) | -2 189 / -2 360 / -4 152 | -6 420 / -12 262 / -26 046 |
| arc growth (the volume thermostat's) | 10 935 / 19 889 / 28 787 | 13 096 / 25 745 / 24 821 |
| subduction erosion (the area thermostat's) | -7 832 / -8 830 / -22 554 | -7 735 / -6 176 / -13 482 |
| CO2 source, raw mean | 2551 / 2729 / 3001 | 2882 / 2774 / 2719 |

Sediment-born continental crust (rock SEDIMENT), late: 0.39% of the surface (0.17 submerged, median -4 m) on main
against 1.15% (0.79 submerged, median -316 m) at slope_k 1000.

Reading:
- **Not sea level.** With the creep the sea is lower, by 40-210 m. That's mostly ice in the colder world, plus
  `sea_cont`: the stripped continental edges hold more water. At equal sea level the land loss would be larger still.
- **Not the coasts starved of sediment.** Creep moves only sea-floor sediment. River incision and hillslopes see the
  sea as 0 m (`kernels.stream_power`, `surface._relief`), so a deeper sea next to the coast doesn't erode land.
- **It is the continental crust going under.** The share of the continental crust standing above the sea falls from
  83% to 76% (seed 1) and from 84% to 74% (seed 3), while its area stays the same or grows. The extra drowned
  continent is (a) old continental margins stripped of their cover (cover on drowned continental crust 5.9 to 4.7 km,
  and the crust below -400 m from 11% to 16-19% of it), and (b) sediment piles on the ocean floor born continental at
  20 km (`crust.birth_and_cratons`, `BECOMES_CONT_KM`): about +0.6 points of the surface, drowned at a median -316 m.
  The area thermostat holds the continental area near its target, drowned rises included, so the land-standing part
  shrinks. That is (b). (a) is the margin itself deepening, which is what the creep is for, with the coastal lowland
  (0-500 m, from 43% to 27% of the continent) going under with it as highstands and glacial cycles pass.
- **Weathering and CO2 don't drive the land loss.** They follow it (part 2).
- **Bookkeeping:** the creep conserves sediment volume (`tests/test_sea_creep.py`). But the sea level doesn't count
  the water that sediment on oceanic crust displaces: `earth.sea_tect` reads only the floor's age, and
  `continent_water` only the continental crust. So moving sediment from a continental shelf to the ocean floor lowers
  the sea by the continent's extra held water (`sea_cont` -21 to -45 m, seed 1), when it should leave it nearly
  unchanged. This hides part of the land loss rather than causing it. It is also a main-wide gap: main's oceanic
  crust carries a mean 181-186 m of sediment rise late in the run (~0 at the start), worth roughly +125 m of sea level
  that main never counts. That would change main's calibration, so it isn't fixed here (draft
  `draft-sea-level-ignores-ocean-floor-sediment`).

## 2. Why the world cools

Late means, seed 1 / seed 3, main against slope_k 1000. The source and sink are against their references (frozen at
300 Myr, `earth.REF_FREEZE`):

| | main | slope_k 1000 |
|---|---|---|
| source / its reference | 1.12 / 1.24 | 0.97 / 0.92 |
| sink at the reference CO2 / its reference | 0.98 / 1.10 | 0.90 / 0.89 |
| source reference | 2680 / 2458 | 2812 / 3272 |
| pCO2 (ppm) | 1290 / 1120 | 789 / 750 |
| late dT (C) | +1.86 / +1.50 | -1.71 / -1.77 |
| land T (C) | 11.9 / 11.7 | 5.3 / 4.7 |

Steady CO2 sits where the sink, scaled by the CO2 law, equals the source. So ln pCO2 goes with ln(source / sink),
each against its reference. The sink falls with the land (-8% and -19%), which on its own would *raise* CO2. The
source falls more (-13% and -26%), so CO2 falls. The source falls against its reference because the reference was
learnt high. During the spin-up (0-300 Myr) the creep is draining the start-up continents' thick margin cover fast,
and the volume thermostat makes up the lost volume with arcs: +20% arc growth, and +13% raw source over 0-300 Myr on
seed 1. Late in the run the drowned rises are born continental (born 3.6x main's) and refill the volume instead, so
arc growth falls 14% below main's while the reference keeps the spin-up's level. The cooling is the arc CO2 source
following the continental volume thermostat, which a sediment process now steers. It doesn't follow from less land.

## 3. Candidates

1. **The arc CO2 source follows the volume thermostat's growth factor** (`earth.global_temperature`: `20 x
   growth`, growth from `crust.thermostats`). Any change to the continental volume budget, by erosion, creep or
   sediment birth, moves the volcanic CO2. Making arc outgassing follow subduction (the slab: convergence times
   trench length, which the model has) instead of the volume top-up would cut the link. It's physical (arc CO2 comes
   from the slab and the mantle wedge, not from how much crust the continent needs), but big: it re-sets the source's
   calibration on main.
2. **Count the continent-derived sediment on oceanic crust in the volume thermostat's volume.** The thermostat would
   then not answer a transfer that keeps the sediment at the continent's foot. Subducted sediment still counts as
   lost. Narrower than 1, but it also shifts main slightly (main's ocean floor carries 0.42 km of cover, about 1.7%
   of the continental volume).
3. **Rises born continental.** A 13 km pile on ocean crust becomes "continental" at 20 km and enters the area
   thermostat as drowned continent. A rise is continental-margin sediment, but its crust is oceanic. Keeping it
   oceanic for the area thermostat (or counting only land-standing crust) would stop rises from using up land area.
   It's narrow, and it touches only sediment-born cells, which are 3x as many with the creep.
4. **Lower K (300 rather than 1000).** It halves the creep's transfer (12 300 against 23 600) and the land loss
   (-2.0 / -1.2 points against -2.1 / -3.1), and its cooling is mixed (dT -1.3 / +2.6 on seeds 1 / 3). This is a
   setting, not a fix (part 5: 29 paired draws at 300).
5. **Sea level counts the sediment on oceanic crust** (the bookkeeping gap above). It's right and should be done, but
   it lowers the land further, so it's no cure for the land loss. It's main-wide and needs its own judge.

**Lean: 1** (arc CO2 from the slab), with 3 as a cheap screen to try first. The cooling is the larger harm (it fails the soft pass), and it
comes from the volcanic source being tied to a bookkeeping thermostat. 3 removes most of what lets the creep steer the
thermostats late in the run. 2 and 5 are corrections that main also needs. None is built here (owner: proposals only). None is a plain bookkeeping error in the creep, and each changes main,
so each needs its own judge. Drafts: `draft-arc-co2-follows-volume-thermostat` (1-3) and
`draft-sea-level-ignores-ocean-floor-sediment` (5).

## 4. The early shelf collapse (draft-l6-shelf-collapses-after-100-myr)

Screen: the judge draw 819014 (offset 0.0005, star_brightening 1), main, every 2 Myr over 80-200 Myr.

| t (Myr) | 90 | 102 | 114 | 126 | 138 | 150 | 162 | 174 | 186 | 198 |
|---|---|---|---|---|---|---|---|---|---|---|
| shelf % of the ocean | 5.02 | 5.15 | 3.55 | 2.61 | 1.47 | 0.98 | 0.79 | 0.64 | 0.83 | 0.72 |
| sea level (m) | 180 | 243 | 268 | 267 | 239 | 206 | 154 | 94 | 51 | 29 |
| continental crust % of the surface | 40.65 | 40.41 | 40.02 | 39.18 | 38.06 | 36.97 | 36.14 | 36.09 | 35.99 | 36.31 |
| continental crust at -60..0 / -200..-60 m (% of it) | 4.7 / 3.6 | 4.9 / 3.7 | 2.8 / 3.1 | 2.1 / 2.3 | 1.2 / 1.3 | 0.7 / 1.0 | 0.6 / 0.8 | 0.5 / 0.7 | 0.6 / 0.9 | 0.6 / 0.7 |
| ... above 500 m | 26.7 | 24.5 | 24.7 | 27.9 | 31.3 | 35.2 | 39.1 | 44.0 | 48.1 | 50.1 |
| land % | 32.18 | 32.57 | 33.30 | 33.68 | 34.05 | 33.70 | 33.31 | 33.28 | 33.22 | 33.58 |
| collision since 82 Myr (km x L5 cells) | 770 | 2085 | 4361 | 7959 | 12951 | 19531 | 25494 | 28402 | 29802 | 30040 |

Over 102-150 Myr the sea level hardly moves (243 to 206 m, and up to 268 in between). Yet the shelf falls from 5.2%
to 1.0%, while collision thickening (+17 000) and overlap resolution (-18 000) take the continental area down by 3.4
points and lift the crust above 500 m from 25% to 35% of it. All 36 draws of the judge's main arm show the same
step: from 100 to 150 Myr, continental area -2.9 points (median; down in 36/36), mean continental crust +2.2 km
(36/36), shelf 4.96 to 1.31% (down by more than 2 points in 33/36), sea level 235 to 137 m (a fall of more than
100 m in 18/36). Across draws, the shelf's fall goes with the area's fall (0.8 points of shelf per point of
continental area) more than with the sea's.

Named process: **the start-up continents' first assembly**. Collision and overlap squeeze and lift the flooded low
plains that made the 100 Myr "shelf", with the sea falling from the start-up's ridge highstand (+235 m at 100 Myr)
as well. It isn't rifting, erosion, isostasy or the brink rule. The 100 Myr shelf was never a built margin. It is
the highstand flooding plains that stand within 200 m of the sea (0-200 m was 30% of the continental crust at
100 Myr).

Candidates, nothing built:
1. The start-up layout (`setup.initial_state`) places continents that assemble within ~100 Myr. That's a design
   choice: a supercontinent cycle from the start.
2. The start-up highstand (+235 m at 100 Myr) comes from the young floor the first breakup makes, measured against
   the starting floor (`depth_ref`). It floods the start-up plains and makes a shelf that the next assembly removes.
3. The slow recovery afterwards (1.3% at 150-250 Myr to 2.7% at 800-1000) is the built margin. The brink fill
   builds shelf one cell at a time, and the sea stands near 0 m (+40 to -80 m) late in the run. That is PW-950's own
   question, not a collapse.
No bug: the drop is real model behaviour.

**Where the eroded rock goes** ([sinkdiag.py](sinkdiag.py), a probe that wraps `surface.erode` and `crust.accrete`
and reads what they return; the same draw 819014, main, km x L5 cells per Myr). Lake = deposit on lake and closed-basin
cells; flood = the rest on land; shelf = sea cells above -400 m; brink = deep cells next to land or shelf; fan = the
other deep cells. Accreted and subducted are the sediment the trenches meet (crust.accrete scrapes half and the slab
takes half, `accretion` 0.5). The five deposit columns add up to the land erosion within 0.1%.

| Myr | eroded on land | lake | flood | shelf | brink | fan | accreted | subducted |
|---|---|---|---|---|---|---|---|---|
| 0-80 | 89.7 | 8.2 | 23.6 | 19.3 | 17.0 | 21.7 | 4.4 | 4.4 |
| 80-100 | 82.9 | 2.2 | 16.8 | 25.6 | 13.3 | 25.0 | 8.6 | 8.6 |
| 100-125 | 83.4 | 5.1 | 19.4 | 17.4 | 14.3 | 27.1 | 7.9 | 7.9 |
| 125-150 | 99.9 | 7.9 | 24.8 | 9.7 | 20.6 | 36.8 | 12.9 | 12.9 |
| 150-200 | 109.0 | 8.2 | 23.6 | 8.2 | 27.0 | 42.0 | 17.0 | 17.0 |
| 200-400 | 90.5 | 2.8 | 15.9 | 12.6 | 25.0 | 34.2 | 14.8 | 14.8 |
| 400-700 | 99.0 | 6.9 | 14.5 | 11.1 | 29.1 | 37.4 | 17.3 | 17.3 |
| 700-1000 | 88.4 | 4.9 | 11.0 | 11.7 | 27.3 | 33.5 | 19.2 | 19.2 |

Over a run, about a fifth of the eroded rock stays on land (floodplains ~15-25%, lakes and closed basins ~5%), an
eighth on the shelf, and two thirds goes past the shelf: ~30% into the brink cells, ~35-40% onto the deep fans. Late
in the run the trenches meet about 40% of the erosion rate as sediment, and half of that goes down with the slab.

So the 100-150 Myr shelf collapse is **not sediment leaving**. River supply keeps up and even grows (83 to 100). No
creep acts on main. The shelf's intake falls (25.6 to 9.7) because the shelf shrinks, so more of the load passes to
the brink and the fans. Subduction takes ocean-floor sediment, not shelf, and it rises only after the shelf is gone.
The cover on drowned continental crust drops from 6.8 to 5.6 km over 100-150 Myr, as the flooded plains it lay on
are lifted out of the sea or folded into the collision. It is **the crust under the shelf changing**: the assembly in
the table above.

## 5. Supporting evidence: 29 paired draws of slope_k=300 alone (stopped judge, not a verdict)

v1-finish-16's L6 draws, rolls 0.0005 (18) and 0.001 (11 of 18), star_brightening 1, through paired_margin.sh. Main
arm complete (36), creep arm stopped at 29. Paired medians, on - main, with bootstrap 95% intervals, over 600-1000 Myr:

| measure | main | slope_k 300 | median diff | 95% CI |
|---|---|---|---|---|
| land % | 34.96 | 33.56 | -1.60 | [-1.85, -1.16] * |
| land % 0-300 Myr | 33.32 | 32.42 | -1.11 | [-1.26, -1.01] * |
| late dT (C) | 0.91 | 0.37 | -0.92 | [-1.97, +0.66] |
| late CO2 index | 0.54 | 0.48 | -0.10 | [-0.36, +0.16] |
| ln source raw, 0-300 Myr | 7.94 | 7.95 | +0.04 | [-0.04, +0.08] |
| ln source raw, late | 7.94 | 7.88 | -0.07 | [-0.08, +0.03] |
| ln source reference | 7.99 | 8.01 | +0.05 | [-0.05, +0.11] |
| ln sink raw, late | 6.48 | 6.37 | -0.12 | [-0.20, -0.04] * |
| weathering land area (w_area) | 0.314 | 0.293 | -0.025 | [-0.030, -0.016] * |
| sea level (m) | -36 | -88 | -52 | [-102, +21] |
| sea_cont (m) | -18 | -30 | -12 | [-16, -9] * |
| sea_ice (m) | -65 | -81 | -21 | [-46, -6] * |

At 300 the land loss is clear and present from the start (-1.1 points over 0-300 Myr). The sea is lower, not higher,
and `sea_cont` falls as in part 1. The source signs match the mechanism of part 2 (spin-up source and reference up,
late source down), but at 300 none of them, nor the cooling, is outside the noise.
