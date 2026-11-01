# PW-950 round 2: necking-zone margins and a continental rise (lane 100)

Diagnosis (written before any run): [diagnosis.md](diagnosis.md). Harness: [margindiag.py](margindiag.py)
(tools/ice_diag.py plus margin numbers every 50 Myr, in memory) and [earth_margin.py](earth_margin.py) (the same depth
numbers for Earth on the model grid, from `data/earth/L<n>.npz`, read-only).

## In plain words

The cliff at the edge of the continents is there because a rift in the model breaks straight through to ocean floor:
the edge of the continent is hardly stretched (beta about 1.07). I made a rift pay for its new floor with stretched
continental crust taken out of the edge (a necking zone, as on real rifted margins), until the edge is thin enough to
break, and made the sediment that falls off the shelf settle first where the slope flattens out (a continental rise).

It helps, clearly but not hugely, and it can't be merged yet. At L6 over three seeds, the share of coast cells with
3 km-deep water in the very next cell falls by a third (23% to 15%; Earth on the same grid 3.5%). The middle depths
(200-3000 m) grow from 12.3% to 14.7% of the ocean (Earth 19.6%), and the coast-to-3 km distance grows from about 250 to
300 km (Earth 600). At L7 (one seed) the cliff share more than halves (20% to 9%; Earth 1.5%). The shelf barely moves,
and the drowned continent's median depth only rises from about -760 m to -650 m, so the ticket's two checkboxes are
still unmet. On the paired climate judge (11 re-rolled draws per arm) the soft pass count is the same or better (10/11
against 9/11), and nothing froze, boiled or lost its ocean. But 3 of the 11 new draws dipped below 100 ppm CO2 at some
point after 300 Myr (lane 92's working definition of a CO2 crash), against none on main. That may be chaos (3 against
0 of 11 is a sign-test p of 0.25), but a hard bar can't be waved through on 11 draws. So both changes sit on the branch
switched off (`neck_km=0`, `rise=0`), and the outputs and goldens are unchanged.

What still makes the cliff, after this: the shelf's sediment front. When rivers build a shelf out, the model fills the
next deep cell right up to shelf level, so the front is always a one-cell wall. Once necking thins the margin, that
wall simply moves out to the new edge (draft below).

## What changed on the branch (both off by default)

- `crust.necking` (param `neck_km`, km; 0 = off): new rift floor next to a plate's own continent is laid as continental
  crust as thick as the edge after thinning. The crust comes from the rift pool first, then from thinning the plate's
  continental cells within `neck_km` of the edge by `exp(-eps w)`, `w = 1 - d/neck_km`, with `eps` solved so the crust
  taken equals the crust laid (conserved: Mohn et al. 2012 p. 23; McKenzie 1978 p. 27). When the next ring would be
  thinner than `MARGIN_MIN_KM` (12 km), the rift has broken up and the floor stays ocean. Thinning is logged as rift
  strain, so McKenzie's thermal sag acts on it. Test: `tests/test_rifts.py::test_necking_pays_for_the_margin_with_thinned_crust`.
- `surface._offshore` (param `rise`; 0 = off): a deep, non-brink cell whose drop to its lowest neighbour is smaller than
  the drop into it from its highest keeps a share `1 - drop_out/drop_in` of the load (flows slowing as the slope eases),
  up to the level that grades the floor between those two neighbours.

## Screens (L6, seeds 1-3, 1 Gyr; means of the 600-1000 Myr samples)

Per seed (s1 / s2 / s3), then the mean. Earth from ETOPO on the same grid (sea = elevation <= 0, as in the runs).

| | shelf % of ocean | 200-3000 m % | 4000-5000 m % | submerged continent median (m) | coast to 3000 m (km) | coast cells with >3 km next cell % | ... within 2 cells % | edge rift strain | land % |
|---|---|---|---|---|---|---|---|---|---|
| main | 2.51 / 3.23 / 2.15 (2.63) | 12.1 / 13.6 / 11.2 (12.3) | 31.1 / 30.9 / 33.0 | -778 / -699 / -812 (-763) | 240 / 267 / 240 (249) | 23.2 / 23.1 / 23.2 | 60.5 / 57.3 / 60.8 | 0.07 | 34.6 / 33.0 / 34.7 |
| necking (neck_km 200) | 3.01 / 3.14 / 1.97 (2.71) | 14.3 / 14.2 / 10.7 (13.1) | 28.7 / 28.9 / 33.8 | -555 / -565 / -854 (-658) | 333 / 320 / 267 (307) | 14.9 / 15.2 / 15.0 | 46.1 / 49.1 / 54.4 | 0.43 | 33.8 / 33.9 / 35.2 |
| necking + rise | 3.36 / 2.82 / 3.08 (3.09) | 15.9 / 13.9 / 14.2 (14.7) | 28.4 / 31.8 / 31.2 | -573 / -724 / -664 (-654) | 320 / 280 / 307 (302) | 14.8 / 16.3 / 13.9 | 49.5 / 52.5 / 48.4 | 0.46 | 33.6 / 34.4 / 33.6 |
| Earth on L6 | 6.21 | 19.6 | 31.8 | | 602 | 3.5 | 22.0 | | 27.8 |

L7, seed 1, 600 Myr (means of the 300-600 Myr samples): main shelf 1.09%, 200-3000 m 8.0%, submerged continent
-995 m, coast to 3000 m 137 km, cliff next cell 20.2%, within 2 cells 50.9%, land 34.5%; necking + rise: 2.13%,
10.1%, -666 m, 189 km, 8.9%, 29.4%, land 31.1% (-3.4 points). Earth on L7: 7.02%, 18.8%, -, 481 km, 1.5%, 9.0%, 27.8%.

Rifted margins only (boundary cells whose continental side rifted in the last 150 Myr; crust km | elevation m at
hops -3, -2, -1 continental and +1 oceanic):

| | crust | elevation |
|---|---|---|
| main, L6 s2, 400 Myr | 33.2 / 30.1 / 25.4 / 9.6 | +164 / +63 / -161 / -3990 |
| necking, L6 s2, 400 Myr | 32.6 / 26.8 / 21.6 / 12.1 | +386 / +127 / -411 / -3542 |
| main, L7 s1, 600 Myr | 30.6 / 27.6 / 24.9 / 11.0 | +148 / +30 / -183 / -3751 |
| necking + rise, L7 s1, 600 Myr | 28.1 / 23.2 / 19.3 / 12.8 | +71 / -97 / -798 / -3333 |

So the necking works as designed: the edge strain goes from 0.07 to ~0.45, and the margin thins seaward over several
cells. But the edge cells' "crust" is crust plus sediment, and the shelf-brink fill of PW-818 piles several km of
sediment on the thinned edge until it stands near shelf level. The step therefore stays at the continent-ocean boundary
(~3.1 km at L6 and ~2.5 km at L7, against 3.8 and 3.6 km on main) instead of spreading into a slope.

Hard bars on the 9 screen runs (tally.py): no frozen, boiled, ocean-loss or CO2-crash runs in any arm.

## Paired judge (v1-finish-16 draws, roll 0.0005, the first 11 of the 18 per arm)

Arms: `base` = main at `cb366840` (a frozen copy), `on` = the branch with `neck_km=200`, `rise=1` as defaults.
Stopped at 11 paired draws for time (load 45-65 on the box; ~35 min per draw).

| measure | main | on | median on - main | 95% CI | moved |
|---|---|---|---|---|---|
| end T (C over pre-industrial) | 0.54 | -0.02 | -1.52 | [-5.62, +3.29] | |
| late dT | 2.24 | -0.90 | -2.63 | [-5.40, +2.06] | |
| late CO2 index | 0.77 | 0.36 | -0.39 | [-0.73, +0.51] | |
| land % | 35.1 | 34.5 | -0.41 | [-1.27, -0.20] | * |
| trees % | 36.2 | 33.0 | -3.5 | [-7.2, +1.5] | |

Soft pass 9/11 (main) vs 10/11 (on). Hard bars (tally.py): frozen 0/0, boiled 0/0, ocean loss 0/0, **CO2 crash 0/11
vs 3/11** (pCO2 minimum after 300 Myr 85, 69 and 82 ppm, in draws 53669 at -0.001, 583167 and 619496; each recovers to
122-249 ppm by the end). The volcanic source (`src ref` +0.05) and weathering sink (`sink ref` +0.00) references don't
move, and necking doesn't change the new-floor count that feeds the CO2 source (`newc` is counted before the margin is
laid), so I see no direct mechanism. A second roll (0.001) of both arms would tell chaos from signal. Not run here
(~3 h more at the 10-core cap).

## What was tried, why it isn't enough, what next

1. Necking (C1): sound and crust-conserving, clearly softens the cliff (the next-cell share falls by a third at L6 and
   by more than half at L7), but the bands move only a little. The drowned continent's median stays at about -650 m
   (target -100..-500), and the shelf share stays about 3% at L6 and 2% at L7.
2. Continental rise (C2): adds about 1.5 points of the 200-3000 m band at L6 on top of necking (2 of 3 seeds).
3. Not tried: wave-base planation (C3, no source read); water-loaded isostasy (lane 23: wrong sign).
4. Next (draft `draft-clinoform-front-has-no-foreset-slope`): give the brink fill a foreset slope, so the shelf front
   is a few-degree wedge set in km rather than a one-cell wall. With necking already thinning the margin, that is the
   piece that should turn the step into a slope. Then re-judge necking + rise + foreset over two rolls, with the CO2
   crash count as the deciding check (draft `draft-necking-margins-judge-co2-dips`).

Commands (scratch under the lane's scratchpad `l100/`, deleted at the end):
`diag.sh CODE OUT CPUS SEED MYR LEVEL THREADS [--set neck_km=200 rise=1]` runs margindiag;
`MAXSIM=5 THREADS=2 taskset -c ... bash docs/review/base-climate/v1-finish-16/paired.sh CODE OUT ARM 0.0005`;
`uv run python docs/review/base-climate/v1-finish-16/pjudge.py OUT base on`; `docs/review/v1-cut/tally.py`.

# Round 3 (lane 100c, 2026-11-01): sea-floor sediment creep

Diagnosis: [diagnosis-foreset.md](diagnosis-foreset.md) (and its addendum on K). Code: `surface._creep`, param
`slope_k` (km2/Myr; 0 = off, the default; goldens unchanged); tests `tests/test_sea_creep.py`.

## In plain words

Sediment on the sea floor now creeps slowly downhill, faster in shallow water than in deep, the way stratigraphers
model how margins build out. Only loose sediment moves, and none is lost or made. It changes the continental edge a
lot: on the 36-draw climate judge, coast cells with deep (>3 km) water in the very next cell fall from 23% to 6.5%
(Earth 3.5%), and the middle depths (200-3000 m) grow from 12.9% to 20.0% of the ocean (Earth 19.6%). The shelf itself
doesn't widen (2.6%, Earth 6.2%). But the judged arm (necking + rise + creep together) also came out about 2 C cooler,
with 3 points less land and 3 fewer passing worlds (26/36 against 29/36). That is within the judge's noise, but it is
not "not worse", so it stays switched off. The screens show the creep itself drowns land, so the next step is to judge
the creep alone and find where the land goes.

## Mechanism

Across every sea-sea edge, a flux `K(d) x drop / iso` km of cover moves from the higher cell to the lower, with
`K(d) = slope_k x 200 / (d + 200)`, d the donor's water depth (Mitchell & Huthnance 2008, K ~ 1/d). Default
proposals: 300 (Jordan & Flemings' 100-1000 m2/yr, log-middle) or 1000. It is explicit, with substeps keeping
`K dt / d^2 <= 0.1`. A donor gives at most its cover minus lava flows, and its ingredients go pro rata. The sediment
arrives as mud, and `sediments()` gives it its sand share. What a cell lost is booked as eroded cover, so the strata
lose their top. It is not counted as weathering (`sim.removed` is unchanged).

## Screens (L6, 1 Gyr, default settings; means of the 600-1000 Myr samples; s1 / s3)

Five tuning arms (k = slope_k): k300 and k1000 on top of round 2 (neck_km=200, rise=1), k300 and k1000 alone, and
rise + k300. Main and round 2 reproduce round 2's numbers exactly.

| arm | shelf % | 200-3000 m % | 4000-5000 m % | coast cells >3 km next cell % | ... within 2 % | coast to 3000 m km | land % | pCO2 min after 300 Myr |
|---|---|---|---|---|---|---|---|---|
| main | 2.51 / 2.15 | 12.1 / 11.2 | 31.1 / 33.0 | 23.2 / 23.2 | 60.5 / 60.8 | 240 / 240 | 34.6 / 34.7 | 253 / 165 |
| round 2 (neck + rise) | 3.36 / 3.08 | 15.9 / 14.2 | 28.4 / 31.2 | 14.8 / 13.9 | 49.5 / 48.4 | 320 / 307 | 33.6 / 33.6 | 160 / 144 |
| k300 | 2.38 / 2.17 | 16.5 / 14.0 | 29.9 / 30.5 | 11.6 / 11.7 | 37.9 / 38.7 | 360 / 360 | 32.2 / 33.5 | 163 / 171 |
| k1000 | 3.11 / 2.80 | 21.1 / 19.6 | 25.8 / 27.8 | 10.2 / 9.2 | 29.4 / 30.9 | 400 / 373 | 31.8 / 30.8 | 123 / 157 |
| rise + k300 | 2.15 / 2.63 | 15.5 / 15.9 | 29.2 / 29.6 | 11.1 / 11.4 | 38.6 / 39.7 | 360 / 360 | 33.2 / 32.7 | 144 / 215 |
| round 2 + k300 | 3.58 / 3.01 | 19.8 / 17.2 | 27.0 / 29.3 | 7.5 / 6.6 | 31.4 / 28.8 | 360 / 373 | 31.8 / 32.0 | 98 / 106 |
| round 2 + k1000 | 2.69 / 2.41 | 19.5 / 20.5 | 27.0 / 27.0 | 5.1 / 6.5 | 21.7 / 24.4 | 468 / 468 | 32.5 / 30.8 | 159 / 153 |
| Earth on L6 | 6.21 | 19.6 | 31.8 | 3.5 | 22.0 | 602 | 27.8 | |

Best on the margin numbers: round 2 + k1000, which was judged. Lane 100d traced the land loss and the cooling: [diagnosis-land.md](diagnosis-land.md).

## Paired judge (v1-finish-16's 18 L6 draws x rolls 0.0005, 0.001; star_brightening=1)

`base` = main (frozen copy at d43d24a1, all three off); `on` = `neck_km=200 rise=1 slope_k=1000`. Run through
[paired_margin.sh](paired_margin.sh) (paired.sh via margindiag.py). pjudge.py, then tools/hard_bar.py per arm.

| measure | main | on | median on - main | 95% CI | moved |
|---|---|---|---|---|---|
| end T | -0.34 | -1.49 | -0.22 | [-3.59, +2.17] | |
| late dT | 0.88 | -2.16 | -2.24 | [-3.61, -0.58] | * |
| late CO2 index | 0.57 | 0.16 | -0.24 | [-0.51, -0.02] | * |
| land % | 34.98 | 32.14 | -2.83 | [-2.98, -2.52] | * |
| sink ref / src ref | 6.61 / 7.98 | 6.55 / 8.01 | -0.05 / +0.01 | [-0.12, +0.02] / [-0.02, +0.10] | |
| arid % / hot desert % | 22.4 / 8.1 | 17.7 / 5.1 | -4.3 / -3.0 | [-5.3, -2.9] / [-4.0, -2.2] | * |
| land rain (mm/yr) / trees % | 1151 / 34.9 | 1073 / 33.5 | -43 / -1.7 | [-89, -15] / [-2.1, -0.6] | * |
| shelf % | 2.55 | 2.60 | -0.02 | [-0.28, +0.25] | |
| 200-3000 m % | 12.89 | 19.98 | +7.43 | [+6.68, +7.67] | * |
| 4000-5000 m % | 30.95 | 27.62 | -3.07 | [-3.63, -2.28] | * |
| coast cells >3 km next cell % | 22.81 | 6.52 | -16.0 | [-16.5, -15.6] | * |
| ... within 2 cells % | 59.86 | 25.17 | -34.4 | [-35.2, -33.3] | * |
| coast to 3000 m (km) | 240 | 437 | +187 | [+174, +201] | * |
| submerged continent median (m) | -785 | -733 | +52 | [-64, +78] | |

Pass count: main 15/18 + 14/18 = 29/36; on 14/18 + 12/18 = 26/36 (both 22, main only 7, on only 4; McNemar p 0.55).
Glacial maximum 22 against 28. Hard bars (hard_bar.py): frozen 0/0, boiled 0/0, ocean loss 0/0, CO2 crash (below the
compensation point) 0/0. Secondary: pCO2 < 100 ppm 3/36 against 6/36, end pCO2 outside 180-600 10 against 16.

Reading: the margin numbers moved strongly toward Earth on every draw, with no hard failure. But the soft pass is 3
lower (the bar is "not worse"), and the world is cooler with less land. So it is **not a clear gain, and not proposed
for defaults-on**. Less land would usually warm a world (less weathering), so the cooling probably comes from less
arid ground and fewer deserts, i.e. a changed land layout. Not traced here. Follow-ups: draft-sea-creep-alone-judge
(creep alone, and where the land goes), draft-marine-diffusivity-k-and-depth-law (the K value),
draft-l6-shelf-collapses-after-100-myr (the shelf share drops 5% -> 1.3% between 100 and 150 Myr in every arm, then
recovers to ~2.7% by 1 Gyr).
