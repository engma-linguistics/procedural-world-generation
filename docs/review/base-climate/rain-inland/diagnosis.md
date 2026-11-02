# Lane 120: rain inland (PW-015, PW-026, epic PW-013). Diagnosis and cheap screens, 2026-11-02

Status: **diagnosis and screens only; nothing merged into the model.** Main 3b5c9935. Three candidates screened on
Earth (L6 regional budget, L7 `earth_check`) and two L6 seeds. The code is parked as a patch
([candidates.patch](candidates.patch)); every knob in it is off by default.

## In plain words

- **The model doesn't lack inland rain. It has too much of it, and too little on the coasts.** Land 40-60 N gets
  1.6-1.8x the observed rain (Mongolia 3.5x, the Great Plains 1.4x, European Russia 1.5x). Meanwhile the monsoon
  and humid east coasts get about half: SE USA 719 mm against 1329, the Pampas 394 against 943, India 627 against
  1126, Japan 671 against 1683. Sea vapour gets carried *past* the coasts and rains 1000-2500 km inland.
  - So for the crops-and-herds goal, the fix is to move rain from the interiors back to the coasts. It isn't to
    push more rain inland. PW-026's rain side ("maritime air should reach 1000-2000 km inland") is already met:
    in winter, Europe and Russia import about 3x the observed net vapour.
- **The land's total rain is set by how much vapour crosses the coasts.** Any change to how fast the air rains
  only moves the rain somewhere else on the same continent. Lane 58 found this for five levers. This lane found it
  again for two more: a humidity gate on showers, and a warmer air mass above winter inversions.
- **The one new lever that moves the right way is surface friction.** Rough land slows the air near the ground
  more than the sea does. In the model, the wind over land and sea is the same. Sourced from the open papers lane
  62 found, this keeps vapour at the coasts. It brings SE USA 719 -> 809 mm, the Pampas 394 -> 430, SE China
  1061 -> 1114 and E Australia 551 -> 631, and the Sahel 2094 -> 2043. Correlation with observed rain goes
  0.714 -> 0.718.
  - It doesn't dry the interiors, though, and W Europe gets a little wetter. It also can't make up for the other
    sound fix: letting the summer inflow carry only its low layer's vapour (PW-1099). That fix dries the interiors
    but takes the coasts with it. With friction added, SE USA only climbs 338 -> 366-421.
- **That is three strikes.** None of the three candidates moves the import across the coasts. Per the rule, this
  goes to the back of the line. What I'd do next is under Recommendation.

## 1. How the kernel moves vapour now

The vapour model is a one-layer column, carried in physical time:

- `planet/climate.py::compute` builds each half-year's wind and hands the rain the **vapour's wind**:
  - `planet/climate.py::monsoon_wind` gives `wind()`'s zonal belts plus the land-sea pressure wind. Poleward of
    15 deg that wind is 0.9 x geostrophic + 0.45 x the cross-isobar inflow, down the gradient. Inside 15 deg it is
    the down-gradient flow alone.
  - That wind, less `planet/climate.py::polar_drift`, then goes through `planet/climate.py::deflect` (terrain
    steering).
  - **The same wind blows over land and sea. Nothing in it knows about surface roughness.**
- `planet/climate.py::_season_inputs` sets the per-cell rain inputs:
  - **qs**, what the air can hold. At sea it comes from the SST. On land it comes from the air mass: the
    sea-level temperature smoothed over 800 km, less `lapse_q` x the height.
  - **src_q**, 0.98 x qs over the sea.
  - **ls**, the large-scale rain rate. It knows the latitude belts (ITCZ, the subtropical sink, the poles) and the
    storminess. It knows nothing about the wind's convergence (PW-1100).
  - **rhc**, the humidity gate, lowered where storms lift the air.
  - **mse_t / mse_thr**, the showers' instability.
- `planet/climate.py::face_winds` and `planet/climate.py::_transport` move the vapour. The upwind vapour crosses
  each face at the face's wind, plus the storms' poleward drift (`eddy_drift`) and eddy mixing. The scheme
  conserves mass.
- `planet/climate.py::sea_uptake` handles evaporation from the sea, as a bulk exchange into a 500 m layer.
- `planet/climate.py::_rain` runs the kernel:
  - over land, Budyko evaporation of the cell's own rain;
  - rain out of oversaturation at `fex`;
  - large-scale rain at `ls` x (q/qs/rh_c)^3;
  - showers at `cv` x the instability, with humidity entering only as LQ x q in the moist static energy.
- `planet/climate.py::storm_spread` spreads the frontal rain over a storm's area.
- `compute` then rescales the global mean to 1000 mm. The kernel's own total is ~1560 mm (x0.64).

## 2. What lane 58 measured (docs/review/base-climate/moisture-budget/README.md), re-run here on 3b5c9935

L6 `tools/moisture_regions.py` reproduces the model's rain bit for bit, and its numbers match lane 58's to within a
few percent:

- **Land imports too much sea vapour.** Land P 1047 mm against GPCC's 789. Land P - E is 2.26 Sv, against ~1.15 Sv
  of published runoff.
- **The vapour doesn't last long over land.** The kernel's vapour lasts 4.1 days over land and 6.1 over sea. The
  observed residence is 9.9 / 8.7 days over land and 9.2 / 8.8 over sea.
- **Summer, 40-50 N: the land-sea inflow overshoots.** It brings 70-88% of the excess. The cross-isobar inflow
  carries the whole column's vapour, and the summer interiors rain 2.3-4.9x the observed rate per mm of vapour,
  66-89% of it as showers.
- **Winter, 50-60 N: the westerlies import too much.** W Europe +1373, European Russia +961, W Siberia +505 mm/yr,
  against an observed +411 / +284 / +168. The interiors sit *above* saturation as the half-year's mean (q/qs 1.13-1.26),
  so 50-62% of their rain is oversaturation.
- **Coasts:**
  - SE USA in summer is a through-flow: the S face brings +3916 mm in and the N face takes -4183 out, on to NE USA
    (2807 vs 1132).
  - The Gulf and W Atlantic subtropics rain 520-555 mm against 1240-1330.

## 3. Where the model departs from the physics

| departure | evidence | status |
|---|---|---|
| a. No rain from low-level convergence | ls has no convergence term | Lane 62's ascent (PW-1100): right for the winter storm tracks. It doesn't rain the summer inflow at the coasts, because its convergence peaks at the heat lows' centres. Parked |
| b. The vapour rains too fast over land | 4.1 days against ~9. van der Ent & Savenije (2011, ACP 11:1853, ERA-Interim) give depletion times of 3-20 days and precipitation recycling length scales of 3000-5000 km in temperate climates, ~4000 km in a belt across northern Eurasia. North of 45 N in winter the depletion time is under 10 days but the replenishment time over 30 | Not by itself the cause. Supply sets the land total, and rate changes only move the rain (lane 58 c4/c7/c9/c10, and C2 below) |
| c. The cross-isobar inflow carries the whole column's vapour, but in reality the inflow is the friction layer's | PW-1099 | Lane 62's `inflow_bl`: Mongolia 610 -> 258, Great Plains 790 -> 384, NE USA 1569 -> 944, but SE USA 708 -> 338 and the Pampas 396 -> 170. Parked |
| d. Winter maritime air rains as oversaturation once it is over cold land | q/qs 1.13-1.26 in the winter interiors. The air mass's qs follows the cold surface air, but the vapour rides above a surface inversion: Zhang et al. (2011, J. Climate 24:5167) find winter surface inversions over Siberia deeper than 800 m and stronger than 15 K, weak over northern Europe and the Norwegian Sea, all anticorrelated with surface temperature | C1 below: right direction, too small |
| e. **The wind is the same over land and sea** | `wind()` and `monsoon_wind` have no surface roughness. Karger & Bumke (1996) measured a surface-to-geostrophic ratio of 0.86 over the open Baltic, with a 26.8 deg ageostrophic angle. A boundary-layer lecture (Mustansiriyah, p. 71; author not stated) gives typical deflections of 15-30 deg over sea and 25-50 deg over land | C3 below: moves the coasts the right way |

## 4. Candidates, sources and screens

Each run is a whole Earth solve (temperatures, winds and vegetation recomputed), not a kernel re-run.
"mr6" is `tools/moisture_regions.py --level 6 --no-cf`, given as annual mm with (winter, summer) in brackets.
"ec7" is `tools/earth_check.py --level 7` on private copies of the caches. Harness: `withtune.py` (TUNE overrides),
in this lane's scratch.

### C1. The vapour condenses in the air above a winter inversion (`inv_share`)
- **Form.** On land not under ice, wherever the air mass is colder than its latitude's sea surface (zonal mean,
  smoothed over 800 km), inv_share of that chill stays below the inversion. qs is taken that much warmer.
- **Source.** Zhang et al. (2011), quoted in row d. With inv_share 0.5 the inversion is ~10 K over a -25 C interior
  against a -5 C sea, which is in their range.
- **Expected effect.** Less oversaturation rain in Europe, Russia and Siberia, with the vapour carried further east.
- **Result (mr6, 0 / 0.5 / 1.0).**
  - W Europe 1148 / 1098 / 1048 (obs 910).
  - European Russia 916 / 902 / 859 (590).
  - W Siberia 698 / 694 / 682 (503).
  - E Siberia 433 / 446 / 449 (295).
  - ec7 at 0.5: B 25.1, r 0.714, unchanged.
- **Why it's small.** The winter import (conv) hardly moves: W Europe +1373 -> +1283, Russia +961 -> +951. The
  vapour that doesn't rain piles up instead (Russia PW 9.8 -> 11.3 mm, NCEP 9.0) and rains later. W Europe stays
  oversaturated (q/qs 1.17), because it isn't colder than its sea at all. Its excess vapour is warm subtropical
  air from the E Atlantic (62% of its winter rain).
- **Strike 1:** the right direction, but it doesn't move the budget.

### C2. Showers gated by the column's humidity (`cv_rh_a`)
- **Form.** The shower rate per unit of vapour is multiplied by exp(a (r - rh_c)) x rh_c / r, capped at 1, with r
  = q/qs and a = 11.4.
- **Sources.**
  - Bretherton, Peters & Back (2004, J. Climate 17:1517): over the tropical oceans the monthly mean P = exp[11.4 (r
    - 0.522)] mm/day, with r the column relative humidity.
  - Schiro, Neelin, Adams & Lintner (2016, J. Atmos. Sci. 73:4043): the same sharp rain pickup with column vapour
    over the Amazon, because the free troposphere's moisture controls the plumes' buoyancy.
  - Neither paper covers mid-latitude summer convection. That is a caveat.
- **Expected effect.** The dry summer interiors (q/qs 0.34-0.48) would rain less per mm and export vapour.
- **Result (mr6, land only).**
  - Mongolia 610 -> 608 (it rains as large-scale rain instead).
  - Great Plains 790 -> 702 and Central Asia 346 -> 266 improve.
  - **SE USA 708 -> 400, the Pampas 396 -> 266, NE USA 1569 -> 1618 and Canada 1236 -> 1258 go the wrong way.**
    SE USA's column (q/qs 0.57) gets gated, and its vapour is carried on north.
  - Land residence 4.1 -> 4.2 days.
  - Gating the sea too gives the same numbers: the sea's showers fire only above q/qs ~0.85, where the gate is 1.
- **Strike 2:** the wrong way. Supply-limited, as lane 58 warned.

### C3. Land-sea friction contrast in the vapour's wind (`fric_land`), alone and as PW-1099's partner
- **Form.** In `compute`, the friction layer's share of the column's vapour over land moves at fric_land of the
  wind. That share is `inflow_share`: 0.44 in the summer, 0.32 in the winter.
- **Where fric_land comes from.**
  - Linear drag gives |V|/G = cos(turning angle). Karger & Bumke's open sea is 0.86 at 26.8 deg; cos 26.8 is 0.89,
    so the relation holds.
  - The land's 25-50 deg then gives cos 37.5 / cos 26.8 = **0.89** at mid-range and cos 50 / cos 26.8 = **0.72** at
    the rough end.
  - The roughness lengths behind it are in ECMWF IFS CY49R1 Part IV, Table 8.3. Land z0m is 0.013-2 m; the sea
    Charnock form gives ~1e-4 m. Lane 62 read these (docs/references/drag-sources-pw1120.md). I didn't use them
    numerically.
- **Expected effect.** Continuity of q x u: the vapour slows and piles up where it comes ashore, so it rains at the
  coast and reaches less far inland.

L7 earth_check:

| | obs | main | fric 0.89 | fric 0.72 |
|---|---|---|---|---|
| B % (Kottek 30.1) | | 25.0 | 24.2 | 23.3 |
| exact / group % | | 37 / 70 | 37 / 71 | 37 / 71 |
| log-rain r | | 0.714 | 0.718 | 0.722 |
| land P mean (GPCC 791) | | 1056 | 1067 | 1083 |
| SE USA | 1329 | 719 | 809 | 960 |
| Pampas | 943 | 394 | 430 | 473 |
| SE China | 1460 | 1061 | 1114 | 1189 |
| Japan | 1683 | 671 | 689 | 722 |
| E Australia | 737 | 551 | 631 | 765 |
| India | 1126 | 627 | 640 | 662 |
| Indochina | 1712 | 1604 | 1645 | 1681 |
| Mediterranean | 545 | 414 | 439 | 484 |
| Sahel | 596 | 2094 | 2043 | 1964 |
| Amazon | 2303 | 3428 | 3394 | 3317 |
| W Europe | 903 | 1158 | 1187 | 1231 |
| European Russia | 591 | 885 | 874 | 854 |
| W Siberia | 506 | 700 | 686 | 664 |
| Gobi/Mongolia | 155 | 536 | 529 | 517 |
| Great Plains | 551 | 765 | 777 | 790 |
| Central Asia | 208 | 317 | 334 | 367 |
| SE USA warmest month (NCEP 25.3) | | 30.4 | 29.9 | 29.2 |

- **Mechanism (mr6, SE USA, Apr-Sep).** The N-face outflow drops from -4183 to -3799 mm. The column's vapour rises
  from 25.9 to 27.8 mm (NCEP 33.5), and the land's evaporation from 800 to 1046 (NCEP 1686): the coast recycles its
  own rain again.
- **Costs.**
  - B -0.8 / -1.7 points, the wrong way, mostly Central Asia and the Mediterranean margins getting wetter.
  - Land mean +11 / +27 mm.
  - W Europe +29 / +73: its westerly import piles up at the coast, as lane 58's c5 did.
- **As PW-1099's partner (mr6, inflow_bl on).** SE USA 338 / 366 / 421 for fric 1 / 0.89 / 0.72 (main 708), the
  Pampas 170 / 174 / 180 (396). The interiors stay fixed: Mongolia ~260, the Great Plains ~390. A ~6-15% slowdown
  of the vapour-weighted wind can't make up a 50-75% cut in supply.
- **Strike 3:** as the partner it fails. Alone, it is the only candidate that moved the coasts the right way.

### Two L6 seeds, 1 Gyr (fric 0.89 vs main; land climate sanity)

See section 6.

### Applying the patch
Run `git apply docs/review/base-climate/rain-inland/candidates.patch` against main 3b5c9935. It includes lane 62's
parked patch (`inflow_bl`, `ascent`), which `fric_land` needs for `inflow_share`. It also adds
`inv_share`, `cv_rh_a` / `cv_rh_a_sea` (`planet/climate.py::_cv_gate`, with the matching lines in
`tools/moisture_budget.py::_probe` and `tools/moisture_regions.py::kernel_inputs`) and `fric_land`. All are off;
with them off, the regional probe reproduces the model bit for bit. Screens: `withtune.py KEY=VAL,... tools/X.py
...` runs a tool with TUNE overrides. `summ.py` and `ecsumm.py` turn the outputs into tables; the full
moisture_regions table is [budget_L6_screens.txt](budget_L6_screens.txt). Tests weren't run on the patch: it isn't
merged.

## 5. Recommendation

1. **Three strikes, so PW-015 / PW-026 go to the back of the line.** No merge from this lane.
2. **Correct the framing for the owner: "rain inland" is too much inland and too little on the coasts.** PW-026's
   description (winter cold) is out of date (lane 26). Its rain side is the reverse of its title: the westerlies
   reach 1000-2000 km inland and import 3x. Its acceptance should become "winter import into Europe and Russia
   toward observed", not "reach further".
3. **The friction contrast (C3 at 0.89) is sound and sourced, and it helps every monsoon coast, but it is a small
   step.** Its value is as one piece of a later round. Merging it alone would make the coasts 5-15% wetter (r +0.004)
   while costing 0.8 points of B and leaving the interiors as wet as they are. That's a judgement call; my lean is not to merge it alone (memory: no partial fixes).
4. **What moves the import is the supply side, which is what a v2 design round should look at.**
   - The coasts' vapour lives in the subtropical seas next to them: the Gulf and W Atlantic rain 0.4x GPCP and hold
     0.8x NCEP's vapour.
   - That is PW-015's own option A, a boundary layer under the column, together with the storm-track seas' winter
     evaporation (the sea makes a third of NCEP's).
   - Only once those seas are moist does PW-1099's inflow depth stop starving the coasts. Then friction and the
     convergence ascent (PW-1100) put the rain where the air comes ashore.
   - That's an l/xl round, so it needs the owner's go (needs-decision draft).

Links:
- **PW-1279 (summer heat).** The dry coasts are also the hot ones. SE USA's warmest month cools 30.4 -> 29.9 / 29.2
  C with C3 (NCEP 25.3), through the summer split's evaporative cooling. Part of PW-1279's low-latitude heat may be
  this same rain deficit (India 33.3 C and BWh against Aw). Diagnose PW-1279 with a rain-swap check: observed rain
  into the water balance.
- **D34 (plant growth).** Its NPP checks on Earth will inherit these regional rain errors. Mongolia, the Sahel and
  E Africa are 3.5-4x too wet, so too productive; SE USA, the Pampas and India are 0.5x, so too poor. Read D34's
  regional misses against this table before tuning plants.

## 6. L6 seeds

`tools/health.py --l6 1 2 --l7 --myr 1000`, main against fric_land 0.89, on scratch stores. Means are over keyframes
from 800 to 1000 Myr; land rain is over ice-free land.

| seed | run | late dT C | arid % | trees % | NPP | land ice % | land rain mm | largest lake Mkm2 (whole run) |
|---|---|---|---|---|---|---|---|---|
| 1 | main c13634 | 2.3 | 20.1 | 44.8 | 263 | 4.7 | 1267 | 1.97 |
| 1 | fric f1f880 | 3.6 | 20.5 | 47.4 | 252 | 1.5 | 1214 | 3.35 |
| 2 | main 243ef8 | 6.1 | 26.8 | 41.6 | 250 | 0.6 | 1180 | 2.18 |
| 2 | fric f752a9 | -0.1 | 25.1 | 39.4 | 194 | 3.3 | 1166 | 5.29 (giant-lake frames 7.8%) |

- **Land climate is sane in both arms.** Arid, trees and rain are within each other's spread, and nothing fails
  hard.
- **The late dT differences are chaotic divergence.** One draw per arm, and seed 2 differs by 6 C. They can't be
  read as the change's effect (memory rule: re-rolled draws before calling signal).
- **One flag for a later judge.** Seed 2's fric run has giant-lake frames (7.8%) and a 5.3 Mkm2 lake. Wetter coasts
  could fill big basins, or this could be the same chaos. Any merge of fric_land needs the pooled judge.
- The scratch runs have been deleted.

## Sources read for this note
- Zhang, Seidel, Golaz, Deser & Tomas (2011), Climatological characteristics of Arctic and Antarctic surface-based
  inversions, J. Climate 24, 5167-5186 (staff.cgd.ucar.edu/cdeser/docs/zhang.polar_sfcinversions.jclim11.pdf).
- van der Ent & Savenije (2011), Length and time scales of atmospheric moisture recycling, Atmos. Chem. Phys. 11,
  1853-1863.
- Bretherton, Peters & Back (2004), Relationships between water vapor path and precipitation over the tropical
  oceans, J. Climate 17, 1517-1528 (aos.wisc.edu/~lback/wvpprecip.pdf).
- Schiro, Neelin, Adams & Lintner (2016), Deep convection and column water vapor over tropical land versus tropical
  ocean, J. Atmos. Sci. 73, 4043-4063 (NOAA IR 28953).
- Karger & Bumke (1996), Spatial extension of coastal impact on the mean surface wind over the Baltic Sea
  (oceanrep.geomar.de/id/eprint/8127).
- Lecture chapter "13. Fundamental Forces", Mustansiriyah Univ., p. 71 (author not stated).
- Also opened: Steinbring et al., arXiv:1007.1680 (Eureka inversion 8-14 K at ~800 m, citing Kahl et al. 1992 and
  Serreze et al. 1992). Not used for numbers.
