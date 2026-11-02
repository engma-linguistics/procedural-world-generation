# Land zoom practice sections: seams between 4000 km neighbours (PW-1300, epic PW-1299)

Lane 116, 2026-11-02. World `dba204` (Earth-like B, L7, finished). No code under `planet/` changed. Re-measure with
`uv run python docs/review/land-zoom/seams.py ZOOM_A ZOOM_B --name X` then `python docs/review/land-zoom/table.py`.

## In plain words

I zoomed ten 4000 km sections of Earth-like B and compared the places where neighbours meet. The headline:

1. **Cost is the first wall.** One 4000 km section at 1 km/px took **2 h 48 min and 110 GB of RAM** (peak). At 2 km/px it takes
   20-60 min and 22-40 GB. Tiling an Earth-like's land (~15-20 sections) at 1 km is ~2 days of one-at-a-time compute and
   room for one job at a time on this machine. Because of that, every seam below was measured at **2 km/px** (2000 px
   squares), not the ~1 km the ticket suggested; one 1 km section was run only to cost it. (PW-1303)
2. **Coasts and big landforms line up** where both sections are built from the same coarse world: coast breaks are 0-0.5 per
   100 km and the two zooms put the sea in the same place. That is by construction, not by luck: each zoom keeps the
   coarse cells' means and noise is sampled at 3D planet positions.
3. **Heights agree in lowlands and disagree in mountains and ice.** Median height difference is 7-20 m on plains and
   coasts, 58 m at the desert/dune edge, and **300-480 m (p95 1.9-3.4 km) on the ice-covered range**, with the
   two sections' mountain relief arranged differently (the difference picture is red/blue blotches the size of valleys). The
   difference grows toward each zoom's own edge: the 4000 km square is cut with a "halo" and rivers/terrain near its edge are
   less settled than 100+ km inside. (PW-1301)
4. **Rivers are the clearest break.** Where a river crosses a seam, one zoom often has it and the other does not (within
   3 km): 0.0-0.8 unmatched crossings per 100 km of seam (west block seam, A edge: 30 of 102 crossings unmatched; range seam, A edge: 12 of 17).
   Matched crossings sit a median 0.5-3 km apart (worst 11.5 km), with discharge within ~2x (median |log2| ratio 0.04-1.0).
   Rivers here are anything >= 100 m3/s on land; the break counts rise toward each zoom's own edge. (PW-1302)
5. **The squares do not tile on a sphere.** "East of a section" is not a neighbour square: two sections 3800 km apart along a
   bearing of 90 degrees are rotated against each other and shifted (the SE block section's centre ended 4.5 degrees
   of latitude north of the SW one's), so the overlap is a wedge, not a band, and a "2x2 block" built by stepping east
   then north closed with an overlap of 871 km on its last edge instead of 200 km. The next lane needs a real tiling (PW-1301).
6. Biome class differs 7-36% between the two zooms at the same ground (the vegetation per pixel is noisy; 31-36% on
   the west block seam, where it is a forest/grassland boundary). Landform class is nearly the same (0-6%), since it is the
   coarse cell's own.
7. One odd artifact: a thin arc ring in the open sea of the coast zoom A (picture row 1, and the bright red arc in the
   difference row of `seam-coast.png`) that B does not have; draft filed.

## Geometry (how a regional zoom's square sits on the sphere)

`planet/zoom/regional.py::Frame` is an **azimuthal equidistant** projection around the zoom's centre (lat0, lon0): pixel
(col, row) is x = (col + 0.5 - nx/2) * res east, y = (ny/2 - row - 0.5) * res north of the centre, in km along the sphere
from the centre (not a lat/lon box). So a "4000 km section" is a 4000 km square in that plane: north is up only on the
centre meridian, the square's edges are not great circles or parallels, and the coverage is exact only near the centre
(the metric distorts away from it, little at 2000 km). `zoom()` limits: 10-5000 km, size/res <= 4096 px, so 4000 km at 1 km
is 4000 px, 16 M px.

My tiling: neighbour centre = the point 3800 km from this one along a start bearing (90 east or 0 north) on a great circle
(`Frame(lat,lon).to_sphere`), so squares **overlap by ~200 km** (100 km each side of the line halfway between the centres,
the "bisector" great circle). Overlap is the right choice for a first measurement: both zooms cover the same ground there, so
differences are real mismatches, no extrapolation. `seams.py` samples both zooms at the same sphere points (bilinear for
height, nearest for classes) at three stations across the seam: d = -95 km (B's own edge, A 200 km in), 0 (both 100 km in),
+95 km (A's own edge, B 200 km in). Rivers: a crossing is a run of pixels with discharge >= 100 m3/s on land; matched
if the other zoom has a river within 3 km. All numbers are over the length of seam where both zooms have data.

## Sections (all `world:dba204`, 2 km/px unless stated; ids are in `zooms/` and open in the viewer)

| role | ref | zoom id | wall | peak RSS |
|---|---|---|---|---|
| block SW | `world:dba204(-25.0, 65.0)` | 7b69a9 | 22 min 23 s | 28.8 GB |
| block SE | `world:dba204(-20.4657, 101.838)` | a33145 | 21 min 26 s | 33.3 GB |
| block NW | `world:dba204(9.1742, 65.0)` | f6a9c7 | 32 min 14 s | 34.0 GB |
| block NE | `world:dba204(7.5798, 99.5178)` | c9ae66 | 25 min 36 s | 39.9 GB |
| block SW at 1 km/px (cost only) | `world:dba204(-25.0, 65.0)` 4000 km @ 1 km | 69b422 | 2 h 47 min 42 s | 110.4 GB |
| coast A | `world:dba204(40.0, 130.0)` | 2a4463 | 59 min 12 s | 33.9 GB |
| coast B | `world:dba204(32.1271, 171.5504)` | fde691 | 35 min 32 s | 33.2 GB |
| range A (ice-covered range) | `world:dba204(70.0, -180.0)` | 7fd990 | 42 min 26 s | 29.7 GB |
| range B | `world:dba204(51.0267, -116.7369)` | e82f85 | 36 min 54 s | 22.2 GB |
| desert A | `world:dba204(10.0, -120.0)` | 48489d | 20 min 0 s | 32.3 GB |
| desert B | `world:dba204(44.1742, -120.0)` | 50d6af | 41 min 17 s | 22.9 GB |

Walls are with up to six zooms running at once on the 48-core machine (and another lane's sims), so they are upper bounds
of a lone run; RSS is `/usr/bin/time -v` max resident of the whole process. The 1 km run's memory peaked at ~107 GB in
the first ~8 min (terrain stage), then sat at ~48 GB for the long serial landscape stage (one core, ~2 h; its start-to-finish was not logged per stage). 4x the pixels cost ~8x the time and ~3.5x the peak memory.

Why these places (chosen from the world's layers, `elevation`, `flow`, `biome`, by scoring the bisector line of each
candidate pair; scripts in the lane's scratchpad):
- **Block** (SW-SE `blockS`, NW-NE `blockN`, SW-NW `blockW`, SE-NE `blockE`), on the Trojanel landmass at the equator to 10 N: the west edge runs
  along ~10 river crossings with the world's largest flows (up to 1,317 m3/s at world scale), the east edge near 100 E passes
  the world's second-largest river (-1.6, 91.2, 1,659 m3/s) with ~1,540 m3/s, a mid-height range, a coast on the south seam and a desert/savanna
  boundary.
- **coast**: the seam runs across a gulf and a 600 km coast (11 land/sea crossings along the line in the candidate scan).
- **range**: the highest relief in the world (8,000 m of world-scale range along the line), a dense ice sheet, high latitude.
- **desert**: 14-18 desert/ice biome transitions along the line and ~2,100 m of range: a dune-field edge and a mountain front.
9459ad (Earth-like A) was not needed.

## Seam numbers

dh = elevation difference A - B where both are land (m, absolute median and 95th percentile; bias is the signed mean);
dslope = absolute difference of the slope from each zoom's own 1-pixel gradient (degrees); coast breaks = runs where one
zoom has land and the other sea or lake, per 100 km of seam; river breaks = unmatched river crossings (either side) per 100 km of
seam (crossings A/B, unmatched A/B in brackets); matched offset is the distance between matched crossings.
Seam names: `blockS` SW-SE, `blockN` NW-NE, `blockW` SW-NW, `blockE` SE-NE (overlap 871 km: see geometry), `coast`,
`range`, `desert`. Stations: B_edge d = -95 km, middle 0, A_edge +95 km (for `blockE` +-430 km).

| seam | station | line km | median dh m | p95 dh m | bias m | median dslope deg | p95 dslope deg | coast breaks/100km | river breaks/100km (A/B crossings, unmatched A/B) | matched offset km (median/max) | landform mismatch % | biome mismatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| blockE (gap 3129 km, overlap 871) | B_edge | 1898 | 56.5 | 335.5 | 16.9 | 0.82 | 5.30 | 0.05 | 0.16 (15/16, 1/2) | 1.0/2.0 | 0.1 | 1.7 |
| blockE (gap 3129 km, overlap 871) | middle | 3715 | 12.7 | 100.0 | -1.1 | 0.21 | 1.81 | 0.51 | 0.13 (19/21, 1/4) | 0.8/4.0 | 1.0 | 10.1 |
| blockE (gap 3129 km, overlap 871) | A_edge | 1896 | 13.1 | 95.1 | 0.2 | 0.24 | 1.17 | 0.05 | 0.16 (5/7, 1/2) | 0.5/3.0 | 1.7 | 13.6 |
| blockN (gap 3800 km, overlap 200) | B_edge | 1888 | 13.7 | 95.3 | -8.3 | 0.18 | 1.25 | 0.05 | 0.05 (7/6, 1/0) | 1.5/5.0 | 0.9 | 9.8 |
| blockN (gap 3800 km, overlap 200) | middle | 3327 | 15.1 | 137.8 | 3.2 | 0.25 | 1.88 | 0.03 | 0.21 (20/20, 4/3) | 1.0/3.0 | 0.4 | 13.9 |
| blockN (gap 3800 km, overlap 200) | A_edge | 3784 | 21.6 | 138.8 | -4.9 | 0.28 | 1.65 | 0.05 | 0.21 (19/17, 5/3) | 1.0/4.0 | 0.8 | 12.7 |
| blockS (gap 3800 km, overlap 200) | B_edge | 1781 | 10.2 | 47.7 | 1.4 | 0.11 | 0.76 | 0.06 | 0.00 (0/0, 0/0) | -/- | 3.4 | 2.1 |
| blockS (gap 3800 km, overlap 200) | middle | 2186 | 12.2 | 63.8 | 0.5 | 0.16 | 1.17 | 0.18 | 0.32 (2/5, 2/5) | -/- | 3.1 | 7.7 |
| blockS (gap 3800 km, overlap 200) | A_edge | 2583 | 20.0 | 124.9 | 1.3 | 0.22 | 1.43 | 0.35 | 0.31 (5/7, 3/5) | 0.5/1.0 | 2.2 | 8.4 |
| blockW (gap 3800 km, overlap 200) | B_edge | 3926 | 10.1 | 68.2 | 2.4 | 0.13 | 0.86 | 0.05 | 0.41 (43/45, 6/10) | 1.0/11.5 | 0.0 | 36.4 |
| blockW (gap 3800 km, overlap 200) | middle | 3933 | 7.1 | 49.9 | 1.7 | 0.12 | 0.60 | 0.00 | 0.36 (46/48, 7/7) | 0.5/4.0 | 0.0 | 31.5 |
| blockW (gap 3800 km, overlap 200) | A_edge | 3927 | 12.2 | 57.1 | 1.1 | 0.16 | 0.78 | 0.00 | 0.76 (46/56, 10/20) | 1.0/5.0 | 0.5 | 32.6 |
| coast (gap 3800 km, overlap 200) | B_edge | 1702 | 7.2 | 51.7 | -4.6 | 0.14 | 0.83 | 0.06 | 0.29 (7/6, 3/2) | 1.2/2.0 | 6.0 | 10.8 |
| coast (gap 3800 km, overlap 200) | middle | 1956 | 8.6 | 72.6 | -1.1 | 0.13 | 1.21 | 0.36 | 0.41 (8/10, 3/5) | 2.0/4.0 | 2.9 | 10.0 |
| coast (gap 3800 km, overlap 200) | A_edge | 2214 | 12.5 | 33.3 | -6.2 | 0.11 | 0.42 | 0.23 | 0.00 (1/1, 0/0) | 3.0/3.0 | 3.7 | 6.5 |
| desert (gap 3800 km, overlap 200) | B_edge | 3926 | 68.4 | 292.3 | 34.4 | 0.53 | 3.01 | 0.00 | 0.00 (0/0, 0/0) | -/- | 0.7 | 7.2 |
| desert (gap 3800 km, overlap 200) | middle | 3933 | 58.5 | 369.1 | 21.5 | 0.53 | 3.68 | 0.05 | 0.00 (0/0, 0/0) | -/- | 0.3 | 17.4 |
| desert (gap 3800 km, overlap 200) | A_edge | 3927 | 58.5 | 424.5 | -3.3 | 0.54 | 3.62 | 0.05 | 0.00 (0/0, 0/0) | -/- | 1.2 | 12.9 |
| range (gap 3800 km, overlap 200) | B_edge | 1667 | 303.9 | 2743.2 | -342.5 | 1.49 | 9.46 | 0.00 | 0.24 (4/2, 3/1) | 3.0/3.0 | 3.8 | 0.0 |
| range (gap 3800 km, overlap 200) | middle | 1881 | 382.1 | 1878.2 | -186.4 | 2.12 | 11.95 | 0.32 | 0.05 (1/0, 1/0) | -/- | 5.1 | 0.0 |
| range (gap 3800 km, overlap 200) | A_edge | 2098 | 482.5 | 3405.4 | -382.1 | 2.94 | 12.99 | 0.29 | 0.57 (7/10, 4/8) | 0.5/4.5 | 5.7 | 2.7 |

## Pictures

Each `seam-<name>.png` is six stacked strips (along the seam left to right, across it top to bottom, A's side up, ~280 km tall,
white tick = the seam line; dark = no data): 1 elevation of A (shaded), 2 elevation of B, 3 A minus B (red: A higher, blue: B higher,
saturated at 400 m), 4 biome of A, 5 biome of B, 6 rivers (A red, B blue, both white) on land/sea.
`seam-blockS.png`, `seam-blockN.png`, `seam-blockW.png`, `seam-blockE.png`, `seam-coast.png`, `seam-range.png`, `seam-desert.png`.
Seen: in `seam-desert.png` the coast and the mountain front match to the pixel but the dune field east of the front is
laid out in different dune bands in A and B (strong red stripes, up to 400 m); in `seam-range.png` the ice cap's relief does not
repeat; in `seam-blockS.png` B only covers a wedge of A (the tilt).

## Failure modes and which ticket owns them

| what | evidence | ticket |
|---|---|---|
| Squares from "go 3800 km east/north" do not tile: rotated, shifted, overlap wedge or 871 km; no common grid of sections | `blockS` picture, `blockE` overlap 871 km | PW-1301 |
| Relief differs between neighbours, worst in mountains, ice and dunes, and grows toward each zoom's own edge (p95 dh 33-130 m on plains, 290-425 m at the dune edge, 1.9-3.4 km on the ice range) | table | PW-1301 |
| Biome class (per-pixel vegetation) differs 7-36% on the same ground | table | PW-1301 |
| Rivers: crossings present in one and absent in the other, matched ones 0.5-11.5 km off, discharge up to 2x apart; each zoom routes only the water that falls inside its own square | river columns, `seam-blockW.png`, `seam-range.png` | PW-1302 |
| 1 km section = 2 h 48 min, 110 GB; a serial landscape stage (one core) dominates; 4x the pixels is ~8x the time and ~3.5x the memory | cost table | PW-1303 |
| An arc ring artifact in A's open sea (coast A) that B lacks | `seam-coast.png` strips 1 and 3 | draft `draft-zoom-sea-arc-artifact` |

What looked fine: coast position (0-0.5 breaks per 100 km), landform class (0-6% mismatch), median slope difference (0.1-0.5
degrees on plains and coasts, 1.5-3 degrees on the ice range).

Not done (per the ticket): no fixes; world 9459ad, a second 1 km section, and the tolerances (river threshold 100 m3/s,
match 3 km) are left to PW-1301/1302. Draft for the tiling rule: `draft-land-zoom-tiling-geometry`.

## Opening them in the viewer

Zoom ids: 7b69a9 a33145 f6a9c7 c9ae66 69b422 2a4463 fde691 7fd990 e82f85 48489d 50d6af. Two throw-away test zooms I made
(038105, 6df49b) were deleted. Seam scripts: `docs/review/land-zoom/seams.py`, `table.py`.
