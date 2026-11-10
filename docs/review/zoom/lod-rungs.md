# The two close-up rungs under a 4,000 km section: measured (PW-1675, step 2 of `lod-plan.md`)

Lane 284, 2026-11-10. World dba204, section zoom **2a4463** (4,000 km at 2 km/px, centre 40.0, 130.0, north-up, an existing
build: its own build time 3,533.7 s was recorded in its `zoom.json` under load; not re-timed). Every build below was made by
the CLI in a private data root (`PLANET_DATA` pointing at a scratch folder with read-only links to the owner's worlds and the
section), one at a time, `/usr/bin/time -v` for wall time and peak RSS, `du -shL` for disk. Machine: 183 GB, ~91 GB available,
load 7-11, so times are "on a busy machine, up to 8 cores asked, 220-310% CPU used".

## In plain words

**Yes: the 500 km rung is rich enough.** Made by the existing fine pass from the 2 km section, it is not a sharpened copy:
in the mountains it has 24% steeper mean slopes and 40% rougher ground than a regional zoom of the same spot, 27-56% more
river pixels, and detail the section cannot show (it departs from the section's smooth surface by 125 m on average inside, 4.4-57 m
at the edge, by spot). It agrees with the section at its edge (mean height difference within +-2 m, rivers carry
through). It is cheap: **34-53 s, 8.2-10.6 GB, 88-92 MB on disk** each, against ~4 min and 23 GB for the section. The 30 km rung
at 25 m is also cheap (**36-42 s, 8.0-12.2 GB, 124-128 MB**) and also agrees with its parent.

Two caveats, neither decides the question: (1) the fine pass writes **48 layers where the section has 71**; the 25 it
leaves out are the game and human-use ones (fuel, foraging, grazing, timber, fertile, travel, passes, sightlines, harbours,
shore and glacial forms and so on), so a rung opened in the viewer has the terrain, rivers, vegetation and satellite view but
those overlays are blank (filed as a draft). (2) The "pictures" asked for by the plan are not in this report: the images
(1.6-2.9 MB each) live in the scratch folder, which is deleted; the viewer shows any rung from its id if the zooms are rebuilt.

Q3 therefore does **not** need to go to Daniel; the plan's lean (A, fine pass as is) stands.

## The spots

All three are well inside the section (the nearest is ~1,000 km from its edge). Rung 1 = `planet zoom 2a4463 --lat .. --lon .. --size-km 500
--res-km 0.5` (1,000 x 1,000 px, 4x finer). Rung 2 = `planet zoom <rung 1 id> --size-km 30 --res-km 0.025` (1,200 x 1,200 px,
20x finer), centred on the rung 1 spot with the most relief and a river (mountain), the biggest river (river plain), or a
half-land window (coast).

| Spot | Where (lat, lon) | Why |
|---|---|---|
| Mountain range | 35.36, 135.52 (rung 2 at 34.5337, 133.6395) | section land with mean 3,700 m, relief 4,100 m in the 200 km block |
| River plain | 42.38, 138.55 (rung 2 at 40.6881, 137.6636) | the section's biggest river, 34,000 m3/s at the block; the 500 km window is still hilly (76-2,752 m), only the 30 km rung is flat (115-351 m) |
| Coast | 37.93, 126.86 (rung 2 at 37.7917, 127.3750) | land share 0.6; rung 2 is 50.7% land |

## Cost of each build (every figure from the run named)

| Run id | What | Parent | Wall time | Peak RAM | Disk | CPU |
|---|---|---|---|---|---|---|
| 44d6d6 | rung 1 mountain, 500 km @ 0.5 km | 2a4463 | 53.2 s | 10.6 GB | 92 MB | 220% |
| 01f501 | rung 2 mountain, 30 km @ 25 m | 44d6d6 | 40.4 s | 11.8 GB | 128 MB | 306% |
| b20954 | rung 1 river plain | 2a4463 | 42.2 s | 10.5 GB | 88 MB | 259% |
| c7ec81 | rung 2 river plain | b20954 | 42.1 s | 12.2 GB | 125 MB | 308% |
| 61b06a | rung 1 coast | 2a4463 | 34.3 s | 8.2 GB | 89 MB | 238% |
| 7aff6b | rung 2 coast | 61b06a | 36.1 s | 8.0 GB | 124 MB | 254% |
| 80880d | regional 500 km @ 0.5 km, mountain (for comparison) | world dba204 | 66.1 s | 9.4 GB | 129 MB | 244% |
| 0ce324 | regional 500 km @ 0.5 km, coast (for comparison) | world dba204 | 61.8 s | 7.1 GB | 126 MB | 225% |

Both rungs: 34-53 s, 8-12.2 GB, 88-128 MB. A whole chain (section already built, then rung 1 and rung 2 of one spot) is
about 1.5 min and 12 GB at the peak. The section it hangs from is the expensive part (lod-plan: ~4-5 min, 23 GB). Disk for
48 layers at 1,000-1,200 px: ~90-128 MB, so ten visited spots are ~1 GB. Two rungs at once would need ~24 GB; that is within
the shared-machine cap but the RAM guard still applies.

## Seams: the rung's edge against its parent

Method (script not committed, scratch): each child pixel is mapped into the parent's frame; difference = child height minus
the parent's bicubic surface at that point. "Outer 8 px" is the strip the 3D viewer blends; "outer 1 parent px" is 4 px for
rung 1 and 20 px for rung 2. Rivers: parent pixels with discharge >= Q on the child's outer ring, grouped into runs; "carried"
= the child has a channel with at least half that discharge within +-1 parent px of the run ("+-5" in brackets). Rivers that run
along the edge are counted as several runs, which makes the carried share look worse than it is (checked by hand on c7ec81).

| Run (child vs parent) | Height diff, outer 8 px: mean / mean abs / max abs (m) | Outer 1 parent px: mean / mean abs / max abs (m) | Interior: mean / mean abs / max abs (m) | Build's own parent-mean bias, block rms (m) | Rivers at the edge, Q >= | Carried +-1 px (+-5) |
|---|---|---|---|---|---|---|
| 44d6d6 vs 2a4463 (mountain, rung 1) | +2.12 / 57.0 / 677 | -0.28 / 18.4 / 481 | +1.53 / 124.8 / 2,117 | 1.44, 38.83 | 100 m3/s | 8 of 14 (9) |
| 01f501 vs 44d6d6 (mountain, rung 2) | -0.52 / 4.40 / 172 | +1.01 / 17.7 / 179 | +0.41 / 40.0 / 311 | 0.17, 7.88 | 10 m3/s | 4 of 6 (4) |
| b20954 vs 2a4463 (plain, rung 1) | +0.27 / 20.5 / 423 | -0.45 / 6.84 / 324 | -0.02 / 29.5 / 616 | -0.0, 5.65 | 100 m3/s | 21 of 23 (23) |
| c7ec81 vs b20954 (plain, rung 2) | -0.78 / 1.13 / 56.2 | -0.58 / 2.39 / 63.2 | -0.08 / 2.92 / 59.5 | -0.17, 1.27 | 100 m3/s | 0 of 2 (1) |
| 61b06a vs 2a4463 (coast, rung 1) | +0.40 / 18.1 / 452 | -0.32 / 5.80 / 185 | +0.30 / 24.9 / 1,100 | not read | 100 m3/s | 6 of 6 (6) |
| 7aff6b vs 61b06a (coast, rung 2) | -0.03 / 0.29 / 23.4 | +0.14 / 1.32 / 62.4 | +0.11 / 3.23 / 152 | not read | 100 m3/s | 2 of 2 (2) |

Reading it:
- **Mean bias is within about +-2 m everywhere** (parent means are kept). The mean absolute difference at the edge is the
  detail the child adds below the parent's pixel: tens of metres in mountains at 4x, 1-20 m elsewhere.
- Max differences of 172-677 m (mountain), 423 m (plain rung 1) and 452 m (coast rung 1) happen inside the first 8 px (rung 2 on plain and coast: 23-56 m), so the 3D
  viewer's 8 px blend hides the mean but a lone cliff pixel can show: PW-541's box-shaped cuts are the known cause (not
  re-investigated). The max is a single worst pixel.
- **Rivers carry through** except where a river runs along the edge. In c7ec81 the 27,200 m3/s river runs along the parent
  column at the child's east edge, then leaves through the east side 211 px (5 km) before the bottom corner; the two "not
  carried" runs are that river's ring pixels, not a lost river. In 44d6d6, parent runs at rows 107 and 111 (Q 460) have no
  channel in the child within +-1 parent px (child Q = 1), and +-5 px finds 9 of 14: a real but small loss in the worst
  (mountain) case; PW-391 is the open ticket for fine-zoom rivers carrying less than the parent's. No child channel appears
  where the parent has none (0 of 8, 0 of 3, 0 of 7, 0 of 1, 0 of 1, 0 of 2).

## Is rung 1 thin? Compared with a regional zoom of the same spot

A regional zoom is built from the world, not held to the section, so the two are independent landscapes (their heights differ
by hundreds of metres, as in `match.py`'s note); what matters here is what each draws. Same centre, 500 km, 0.5 km/px.

| Measure | Mountain: rung 1 (44d6d6) | Mountain: regional (80880d) | Coast: rung 1 (61b06a) | Coast: regional (0ce324) |
|---|---|---|---|---|
| Layers written | 48 | 71 | 48 | 71 |
| Elevation mean (m) | 3,066 | 3,093 | -407 | -405 |
| Elevation std (m) | 952 | 842 | 1,451 | 1,446 |
| Mean slope (deg) / 95th percentile | 13.7 / 28.0 | 11.1 / 21.8 | 4.0 / 11.4 | 4.1 / 12.5 |
| Roughness (std of height minus 3x3 mean, m) | 53.5 | 38.3 | 17.4 | 20.4 |
| River pixels, Q >= 100 m3/s | 3,817 | 2,439 | 3,958 | 3,065 |
| River pixels, Q >= 1,000 m3/s | 0 | 0 | 1,543 | 163 |
| Mean abs height difference between the two (m) | 405 | | 82.3 | |
| Landform class agreement | 98.9% | | 98.1% | |
| Biome / soil agreement | 62.2% / 66.7% | | 95.6% / 74.6% | |

- Terrain and rivers: the rung is **at least as rich** as a regional zoom at the same size (rougher and steeper in the
  mountains, more river pixels in both spots; at the coast slope and roughness are equal or 15% lower: 17.4 vs 20.4 m).
- The big river at the coast is drawn at 1,000 m3/s+ over 1,543 pixels in the rung, 163 in the regional zoom: the rung
  keeps the section's big river; the regional zoom, built from the coarser world, loses part of it.
- **What the rung lacks** (the layers the section has and the fine pass does not write): barrier_island, building,
  coast_type, fertile, fertile_score, fire_months, foraging, fresh_km, fresh_water, fuel, glacial_form, grazing,
  green_months, harbour, hazards, mud_months, nav_hazard, pass, pass_height, river_nav, shore_form, sightline, spring, timber,
  travel. (Gains two: floor_m, valley_floor.) Landform overlays and reef forms are also not redrawn (`landform_overlay` empty
  in both rungs; nested_fine_zoom.md l.192). The terrain look is not affected.

## `fine.default_size` and the size menu

`default_size` was not wrong in itself: its 500 px sizes (50 km @ 100 m from a 2 km zoom; 12.5 km @ 25 m from a 0.5 km zoom) are
valid and cheaper; the test pins them. What was missing was the **rung sizes on the viewer's size menu**: for a 2 km parent
the menu offered 250 km @ 0.5 km (500 px), not 500 km (1,000 px); from 0.5 km it offered 25 km @ 25 m, not 30 km (1,200 px).
Measurements above show 1,000-1,200 px builds cost no more than 500 px ones in practice (≤1 min, ≤12 GB), so
`fine.size_options` now **adds** the wide size for each resolution a parent of >= 0.4 km offers: 1,000 px for steps under 10x,
1,200 px for 10-20x (500 km @ 0.5 km from 2 km, 30 km @ 25 m from 0.5 km; 1,000 km @ 1 km from 4 km). The default is unchanged. New
constants `WIDE_PX`, `WIDE_PX_BIG_STEP`; asserted in `tests/test_zoom_fine.py::test_size_menu_matches_check`.

## Answer

Rung 1 (500 km at 0.5 km by the fine pass): **yes**, keep plan option A; no question Q3 for Daniel. Rung 2 (30 km at 25 m):
yes. Open points go to the board as drafts: the 25 missing layers on fine zooms; the lost river segments at the mountain
rung's edge; and the pictures (build the three chains again and look at them in the viewer, not done here).
