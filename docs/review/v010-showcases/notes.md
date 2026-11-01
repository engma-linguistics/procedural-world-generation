# v0.1.0 showcase set (lane 110)

Built on main at e55316ad, all six at level 7, `--every 4`, default parameters except the listed `--set`. No code was changed.

## In plain words (for Daniel)
All six showcase planets are built and sliced, and each has its six highlight zooms. Earth-like A and B also have a glacial time zoom and a finished world (the peoples runs need one). Under the hard bar (frozen over, boiled, ocean loss, CO2 crash) none of the six fails: 0 of 6 on each. Three of the six also pass the softer bar (Earth-like A, Earth-like B, land-heavy); the cold, water and hothouse worlds read as icehouse or warm, as the recipe allows. **The peoples runs (dnd on A and B, seven_meals on A) were still running when this file was committed; see "Peoples" below for their state.** Nothing was tuned.

Honest caveats: (1) `tools/hard_bar.py` reads the paired-judge diagnostic files, not stored runs, so I converted each run's stored keyframe stats (every 4 Myr, which is the climate cadence) into that shape with a scratch script. The star term was recomputed from the run's params and dT is true global temperature minus pre-industrial, so the numbers are a close stand-in, not the identical diagnostic. (2) `tools/scorecard.py` runs its own level-6 sims and takes no run, so it was not run. (3) `highlights --at auto` currently picks the finish moment (the run's end when habitable, otherwise the end-of-run or latest warm moment), not the median-frame rule that docs/coordination.md describes; all six landed on the run's end.

## Table
Viewer links: `http://localhost:8765/viewer/?world=<id>.json`. Zoom links: `http://localhost:8765/viewer/zoom.html?id=<id>`.

| Recipe | Run | World (slice) | t (Myr) | Highlight zooms | Hard bar (0 of 4 hard failures) | Soft bar |
|---|---|---|---|---|---|---|
| Earth-like A (seed 11, 1000 Myr) | a19366 | 9459ad | 1000 | 26856c 2ba5b3 ed4e4a c34b36 1a2626 534058 | pass | pass |
| Earth-like B (seed 12, 1500 Myr) | 10fd90 | 848662 | 1500 | 9ae091 0f5a2c 7b8e03 7d6c4d 9a28a0 2b71e4 | pass | pass |
| Water world (seed 13, 2000 Myr) | f27dc1 | b76c8e | 2000 | a90103 f10fa8 77503c b45bc7 0fd2ae 53c5c3 | pass | fail (icehouse, frozen any time after 300 Myr; no habitable moment) |
| Land-heavy (seed 14, 1000 Myr) | fe954c | 036772 | 1000 | 491567 1f6288 6d83c2 cf7117 776876 d7f482 | pass | pass |
| Cold (seed 15, 1000 Myr) | c9f38c | 0c14eb | 1000 | 3dfb13 59a6dd c41d48 29d20c bbc77c d4c970 | pass | fail (icehouse; end -6.4 C vs pre-industrial) |
| Hothouse (seed 16, 1000 Myr) | 5aa5ff | f9c12a | 1000 | 415633 fe6464 41885f 11445c 8df0be 491087 | pass | fail (end +3.5 C; no habitable moment) |

Run names: v010-earthlike-a, v010-earthlike-b, v010-water-world, v010-land-heavy, v010-cold, v010-hothouse. Wall times at 5 threads each (six at once): hothouse 28 min, Earth-like A 50 min, B and land-heavy and cold about 55-60 min, water world about 70 min.

World links: http://localhost:8765/viewer/?world=9459ad.json , 848662 , b76c8e , 036772 , 0c14eb , f9c12a (same pattern).

### Hard-bar detail (tools/hard_bar.py, level 7, converted from stored keyframe stats)
| Run | frozen | boiled | ocean loss | CO2 crash | min pCO2 (ppm, at Myr) | end pCO2 | end dT | peak iced land % |
|---|---|---|---|---|---|---|---|---|
| earthlike-a | - | - | - | - | 195 (848) | 764 | +3.9 | 37.8 |
| earthlike-b | - | - | - | - | 214 (1320) | 398 | +0.3 | 37.0 |
| water-world | - | - | - | - | 40 (1832) | 67 | -9.4 | 46.4 |
| land-heavy | - | - | - | - | 436 (932) | 766 | -0.3 | 23.9 |
| cold | - | - | - | - | 559 (984) | 579 | -6.4 | 44.5 |
| hothouse | - | - | - | - | 203 (992) | 208 | +3.5 | 0.5 |

Totals: frozen over in window 0/6, boiled 0/6, ocean loss 0/6, CO2 crash (D32 B) 0/6. Secondary: pCO2 under 100 ppm 1/6 (water world, 40 ppm at 1832 Myr, still above the plants' compensation point of 17 ppm); 8-fold fall in 50 Myr with end under 1/4 of pre-fall 1/6 (Earth-like A, 848 Myr); frozen any time after 300 Myr 2/6 (cold, water world); end pCO2 outside 180-600 ppm 3/6 (A 764, water world 67, land-heavy 766). Earth-like A ends at 764 ppm with a +3.9 C end, worth a look but not a hard failure. Soft bar: 3/6.

## Glacial time zooms and finished worlds
| For | Time zoom (300 kyr, from the run's end) | Finished world | Moment |
|---|---|---|---|
| Earth-like A | fc5311 (7 glacial events, lowest sea level -73 m) | 899985 | latest interglacial, 286 kyr |
| Earth-like B | 56dee1 (17 glacial events, lowest sea level -111 m) | dba204 | latest interglacial, 202 kyr |

Links: http://localhost:8765/viewer/?world=899985.json , http://localhost:8765/viewer/?world=dba204.json

## Peoples
Started on the finished worlds, 4 tries each (finished by the coordinator after the lane's hand-off). Viewer:
`http://localhost:8765/viewer/?run=<id>&layer=peoples`.

| For | Tree | World | Peoples run | Cultures (all / alive / merged by contact, under states) |
|---|---|---|---|---|
| Earth-like A | dnd | 899985 | b4d502 | 836 / 298 / 399, 22 |
| Earth-like B | dnd | dba204 | a24559 | 773 / 305 / 344, 31 |
| Earth-like A | seven_meals | 899985 | 3c1caf | 871 / 332 / 357, 67 |

`planet cultures` reads sensibly on all three: the largest cultures are the founding peoples (dragon kinds, goblins, hobgoblins,
elves, halflings) and human cultures that split 17-58 kyr ago, with drifting skills (sea craft fading inland, herding lore gained
in open country). Living cultures are about 2.5x the L6 runs' 111-130, from L7's finer cells and the overlapping demes.
