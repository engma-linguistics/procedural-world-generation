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
