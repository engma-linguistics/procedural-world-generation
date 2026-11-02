# Land zoom seams, round 2: the judge of matched sections (PW-1301; epic PW-1299)

Lane 128, 2026-11-02, after lane 127's `seams-round1.md`. World `dba204` (Earth-like B, L7). Code changed:
`planet/zoom/match.py` (owner rule's tiling size, lakes held at their surface, the neighbours' lakes, bare held
ground above the sea, final()'s order), `planet/zoom/stage_landscape.py::lakes` and the lake-sink rule,
`planet/zoom/regional.py` (ctx slot `m_lake`), `tests/test_zoom_match.py` (far-inside station), and the
owner-line stations in `docs/review/land-zoom/seams.py` (`--owner`, `--alone`).

## In plain words

1. **Matched sections meet exactly at the owner line.** On lane 116's four practice seams rebuilt at 4 km/px and on one
   pair of real tiling sections (`py.1.1`, then `py.0.1 --match`), the height difference where the two sections meet
   went from 10-410 m (median; p95 60-2,300 m) to **0.0 m** (p95 at most 0.3 m). The blend across the 80 km ramp is smooth:
   slopes in the ramp are no steeper than the section's own slopes (p95 in the ramp is a little *lower* than
   built alone on every pair). Coasts at the line now agree except for at most one pixel; biomes agree to 0.0-0.2%.
2. **What redrew the coast in the held ground was lakes.** The neighbour's lakes counted as land in the new section,
   and held ground can't hold a lake (it is an outlet), so a lake of the neighbour's that reached the line was dry
   ground, at the depth of the lake's bed, in the new section. Fixed: held lakes stand at their surface, and the new
   section takes the neighbour's lake outlines where it weighs over a half (as it already took the sea's). On the ice
   range seam the coast mismatch at the line went from 0.87% (7 lake pixels) to 0. Two tries; both kept.
3. **A crash fixed on the way.** The coast pair's matched section crashed (vegetation's land test: bare ground below
   the sea). Cause: the neighbour's lake beds (to -60 m) were held as bare ground. Fixed by the same lake-surface change
   and a floor at +0.5 m for bare held ground; `final()` now clamps bare ground on the blended glacier outline, not the
   old one.
4. **The owner rule for tiling sections crashed** (`tiling.choose_n` was called without its overlap): it never ran
   before, since no test matched two tiling sections. Fixed; the turned tiling pair is in the judge.
5. **Matching reaches past the ramp, by design, and fades out.** The held ground is an outlet at the neighbour's
   levels, so a valley draining across the line is graded up from them; the slope fit pulls each coarse cell back to
   its own mean, so the change dies out with distance. On the real pairs (B matched vs B alone, median): 1-86 m at
   80-160 km, 0.1-6 m at 160-300, 0-2 m at 300-600, 0.0 beyond 600 km. Lane 127's test measured 5.4 m 330 km in on a
   level-5 world, whose coarse cells are 4x wider than an L7 world's: the reach scales with the cell (level 5 vs 6,
   below). The test now measures 480 km in (0.24 m) with a 1 m bound; its 15 m bound is gone.

## The judge at 4 km/px (4000 km squares, 1000 px; `seams.py A B --owner [--alone B_alone]`)

Pairs: lane 116's centres (practice.md), A built alone, B built alone and B built matched to A (`--match A`).
`tile`: the tiling's `py.1.1` (A) and `py.0.1` (B), turned sections; owner = the tiling's cell.

| pair | A | B alone | B matched | viewer (B matched) |
|---|---|---|---|---|
| desert (10 N / 44.2 N, 120 W) | d904d6 | 599c28 | a13667 | http://localhost:8765/?world=dba204.json&tab=zoom&zoom=a13667 |
| ice range (70 N 180 / 51.0 N 116.7 W) | fe600a | f4db12 | 59336f | http://localhost:8765/?world=dba204.json&tab=zoom&zoom=59336f |
| coast (40 N 130 E / 32.1 N 171.6 E) | b710fd | 33a72a | 0852e2 | http://localhost:8765/?world=dba204.json&tab=zoom&zoom=0852e2 |
| block W (25 S / 9.2 N, 65 E) | a3a793 | 7ec571 | d7b43d | http://localhost:8765/?world=dba204.json&tab=zoom&zoom=d7b43d |
| tile (py.1.1 / py.0.1) | 683193 | e02373 | 3b412b | http://localhost:8765/?world=dba204.json&tab=zoom&zoom=3b412b |

Each 2.5-4.5 min, 6-8 GB (`/usr/bin/time -v`, five at once). Stations: B's pixels whose centre is d km from the owner
line (d < 0: ground A owns, held in B; the line: the first pixel each side; 0 < d < 80: the ramp), A sampled there
(bilinear heights, nearest classes). dh = |A - B| where both are land; coast = share of points where one has land and
the other sea or lake; biome over points both call land; dslope from each zoom's own 1-pixel gradient.

| pair | station | alone: median dh m (p95) | matched: median dh m (p95) | alone: coast % / biome % | matched: coast % / biome % | alone: dslope p95 deg | matched: dslope p95 deg |
|---|---|---|---|---|---|---|---|
| desert | held -10 km | 87.9 (477) | 0.0 (0.0) | 0.00 / 21.1 | 0.00 / 0.0 | 2.67 | 0.93 |
| desert | **line** | 69.7 (463) | **0.0 (0.0)** | 0.05 / 20.5 | **0.00 / 0.2** | 2.91 | 0.81 |
| desert | ramp +20 | 67.3 (459) | 2.3 (18) | 0.00 / 18.5 | 0.00 / 0.3 | 2.76 | 1.26 |
| desert | ramp +40 | 64.4 (436) | 17.5 (138) | 0.00 / 21.9 | 0.00 / 11.5 | 3.24 | 1.90 |
| desert | ramp +70 | 85.5 (443) | 66.6 (411) | 0.00 / 21.0 | 0.00 / 21.0 | 3.31 | 2.75 |
| ice range | held -10 km | 443 (1796) | 0.0 (0.0) | 0.00 / 0.0 | 0.00 / 0.0 | 9.95 | 5.02 |
| ice range | **line** | 408 (2300) | **0.0 (0.3)** | 0.50 / 0.0 | **0.00 / 0.0** | 12.96 | 4.80 |
| ice range | ramp +20 | 484 (3156) | 20.5 (144) | 0.19 / 2.5 | 0.19 / 0.0 | 12.35 | 4.93 |
| ice range | ramp +40 | 443 (2496) | 172 (872) | 0.00 / 2.4 | 0.48 / 2.2 | 12.31 | 6.72 |
| ice range | ramp +70 | 508 (2616) | 468 (2613) | 0.58 / 2.4 | 2.17 / 2.4 | 12.24 | 12.68 |
| coast | held -10 km | 11.0 (85) | 0.0 (0.0) | 2.03 / 8.2 | 0.23 / 0.0 | 0.72 | 0.37 |
| coast | **line** | 10.8 (86) | **0.0 (0.0)** | 1.22 / 5.4 | **0.11 / 0.0** | 0.82 | 0.49 |
| coast | ramp +20 | 10.0 (95) | 0.4 (3.9) | 4.78 / 10.5 | 0.00 / 0.4 | 0.72 | 0.47 |
| coast | ramp +40 | 11.5 (70) | 3.7 (22) | 3.85 / 4.1 | 3.64 / 2.3 | 0.81 | 0.52 |
| coast | ramp +70 | 9.3 (63) | 8.1 (60) | 1.88 / 6.9 | 1.88 / 5.0 | 1.01 | 0.74 |
| block W | held -10 km | 9.1 (52) | 0.0 (0.0) | 0.00 / 28.1 | 0.00 / 0.0 | 0.41 | 0.22 |
| block W | **line** | 9.5 (59) | **0.0 (0.0)** | 0.10 / 26.6 | **0.05 / 0.1** | 0.43 | 0.20 |
| block W | ramp +20 | 10.6 (55) | 0.5 (3.0) | 0.00 / 28.6 | 0.00 / 1.7 | 0.44 | 0.27 |
| block W | ramp +40 | 11.0 (56) | 4.1 (20) | 0.00 / 30.7 | 0.00 / 16.4 | 0.43 | 0.34 |
| block W | ramp +70 | 10.9 (55) | 10.3 (58) | 0.00 / 30.0 | 0.00 / 30.9 | 0.50 | 0.53 |
| tile | held -10 km | 41.4 (445) | 0.0 (0.0) | 0.61 / 16.9 | 0.00 / 0.0 | 3.26 | 2.61 |
| tile | **line** | 39.6 (373) | **0.0 (0.0)** | 0.09 / 19.0 | **0.00 / 0.1** | 3.74 | 2.63 |
| tile | ramp +20 | 42.6 (420) | 2.3 (25) | 0.80 / 19.9 | 0.05 / 2.1 | 3.98 | 2.42 |
| tile | ramp +40 | 42.7 (492) | 12.1 (169) | 0.44 / 23.0 | 0.33 / 11.2 | 4.00 | 3.09 |
| tile | ramp +70 | 48.6 (552) | 52.3 (505) | 0.44 / 24.8 | 0.44 / 24.8 | 4.76 | 4.50 |

Read: at +40 km (the ramp's middle) the matched B is halfway between A and its own surface, as designed, and its
classes switch there (biome mismatch rises towards the alone value); by +70 it is its own. dslope at held ground is
not 0 although heights are: B's held heights are A's resampled on B's lattice (turned/offset), and a slope from a
resampled raster differs from A's own (the resampling floor). The mosaic shows each place from its owner, so what a
viewer sees across the seam is A at d < 0 and B at d > 0: the "line" row.

Slopes in the ramp (B's own, p95, deg; is the blend steeper than the section built alone?) and how far matching moved
B (B matched vs B alone, median |dh| m (p95; share of pixels whose land/water changed %)), by km from the owner line:

| pair | slope p95 ramp 0-80 matched / alone | slope p95 120-400 matched / alone | 0-80 km | 80-160 | 160-300 | 300-600 | > 600 |
|---|---|---|---|---|---|---|---|
| desert | 4.54 / 4.86 | 3.64 / 3.70 | 44.6 (382; 0.04) | 13.5 (138; 0.00) | 6.1 (117; 0.00) | 1.9 (66; 0.00) | 0.0 (4.7; 0.03) |
| ice range | 16.95 / 18.12 | 19.87 / 19.90 | 351 (1988; 0.68) | 85.9 (789; 0.09) | 2.6 (98; 0.01) | 0.7 (13; 0.00) | 0.0 (3.6; 0.01) |
| coast | 1.23 / 1.47 | 2.76 / 2.76 | 8.2 (62; 1.54) | 1.5 (23; 0.02) | 0.1 (1.9; 0.00) | 0.0 (0.0; 0.00) | 0.0 (1.3; 0.01) |
| block W | 0.95 / 0.97 | 1.22 / 1.18 | 8.2 (46; 0.00) | 2.8 (35; 0.00) | 0.7 (20; 0.00) | 0.2 (20; 0.00) | 0.0 (1.2; 0.00) |
| tile | 6.99 / 7.74 | 6.90 / 6.90 | 1.8 (222; 0.10) | 0.4 (133; 0.00) | 0.3 (60; 0.00) | 0.0 (15; 0.00) | 0.0 (1.1; 0.00) |

Before lane 128's fixes (lane 127's code, same zooms rebuilt; `out127` in the lane's scratch, gone): the heights were
the same at every station on desert, blockW and tile, and within a few metres on the range (ramp +40: 175 -> 172 m);
the coast pair crashed; the ice range seam had 0.87% coast mismatch at the
line (all A-lake vs B-land) and blockW 0.05% (1 px).

## The coast in the held ground (brief item 2)

Breakdown of the line's coast mismatches by water kind (seams.py `coast_pairs`, 'A/B': 0 land, 1 sea, 2 lake): on
lane 127's code every one at the line was **A lake / B land** (range 7 px, blockW 1 px); desert had none at 4 km
(lane 127's 0.4% was on its 1000 km in-memory pairs). Causes, both in the lake stage:
- `match.sources` made the neighbour's lakes land (`land = water != 1`) and held its *elevation* layer there, which is
  a lake's bed (to -60 m on these pairs, -830 m in the tile A's deepest lake);
- held ground joins the region's edge (an outlet) and `lakes()` takes no candidate on the edge, so the new section
  never had a lake there; a lake whose pixels are mostly held then failed the "lake fragment without an outlet" rule.
Fix (try 1): sources hold lakes at their surface (`elevation + lake_depth`); `match.lakes()` gives the lake outline
the neighbour's where its weight is over a half (held ground included; the square's own edge excluded). Try 1 left the
range's 7 px: they lay under this section's first glacier outline (lakes avoid it). Try 2: the first glacier outline
gives way to the neighbour's lake there (its ice is the neighbour's anyway, `final()`), and the lake-sink rule spares a
lake mostly on held ground (its outlet is the neighbour's). Range line: 7 px -> 0. Left: blockW's 1 px, a neighbour's
lake fragment smaller than the 3 px minimum on this lattice; and lakes in the inner ramp (w < 0.5) are this section's
own (range +70: 12 px of B lake on A land, a lake now continuing across the switch line).

## The far-inside test bound (brief item 4)

Lane 127 loosened `test_matched_section_meets_its_neighbour`'s far-inside bound from 5 to 15 m after measuring 5.4 m.
Stage attribution on the test's own synthetic pair (`round2/far_diag.py`: B alone vs B matched, same
frame, snapshot after every stage, median |dh| on land by km from the owner line):

| | 0-80 | 80-160 | 160-240 | 240-320 | 320-400 | 400-600 |
|---|---|---|---|---|---|---|
| every stage before `landscape_loop` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| after `landscape_loop`, level 5 (~220 km cells) | 212 | 64 | 29 | 9.7 | 3.1 | 0.25 |
| final, level 5 | 251 | 101 | 33 | 9.4 | 3.0 | 0.27 |
| final, level 6 (~110 km cells) | 137 | 31 | 9.4 | 1.9 | 0.44 | 0.04 |

So all of it is made by the landscape pass, and its reach halves when the coarse cells halve: the held ground is an
outlet at the neighbour's levels (a basin that drains across the line is graded up from them), and the slope fit
(`fit_c`: C per coarse cell, smoothed over 0.35 of a cell) with each cell's mean kept pulls the change back cell by cell.
That is the mechanism working as designed (valleys run down to the neighbour's ground), not a leak. The test's far
station was 330 km in, 1.5 level-5 cells: 5.4 m there is the expected tail. Along the test's line: 5 km 275 m, 200 km
33 m, 330 km 5.4 m, 400 km 0.75 m, 480 km 0.24 m, 550 km 0.31 m. The test now measures at 480 km (inside B's square)
with a **1 m** bound. No other bound changed.

On real L7 pairs basins are many cells long, so the tail is longer in cells (0-2 m median at 300-600 km, p95 up to
66 m at the desert's mountain front, where a river basin crosses the line) and 0.0 beyond 600 km.

## The 1 km check (brief item 3)

The tiling pair at 1 km/px (4000 x 4000 px), one at a time: `py.1.1` alone, **34d0a5** (27 min 20 s, peak 103.7 GB),
then `py.0.1 --match 34d0a5`, **8f5874** (30 min 9 s, peak 107.3 GB; 11.2% of its pixels held, 2.3% in the ramp).
Both ran beside another lane's sims (load ~50 on 48 cores), so the walls are above lane 122's 16 min and the peaks
above its 86 GB: budget ~110 GB for a matched 1 km section. No 1 km "alone" B was built (another 30 min / 105 GB); the
alone numbers at 4 km above stand in. Viewer:
http://localhost:8765/?world=dba204.json&tab=zoom&zoom=8f5874 (and zoom=34d0a5).

| station (1 km, tile) | n land | median dh m | p95 dh m | dslope p95 deg | coast % | biome % |
|---|---|---|---|---|---|---|
| held -50 km | 7876 | 0.0 | 0.0 | 3.02 | 0.00 | 0.0 |
| held -10 km | 7888 | 0.0 | 0.0 | 2.90 | 0.00 | 0.0 |
| **line** | 7689 | **0.0** | **0.0** | 2.95 | **0.00** | **0.2** |
| ramp +20 | 6904 | 1.7 | 16.5 | 2.99 | 0.00 | 1.1 |
| ramp +40 | 6850 | 11.5 | 113 | 4.74 | 0.37 | 9.5 |
| ramp +70 | 6758 | 33.9 | 359 | 7.05 | 0.07 | 22.4 |

Slope p95 in the ramp 12.68 deg vs 12.69 inside (120-400 km): no steps. The +40 km coast mismatch (27 points, A land /
B sea) is the mid-ramp coast switch (draft below). Same picture as at 4 km.

Zoom ids (all kept, all cited): 4 km d904d6 599c28 a13667 fe600a f4db12 59336f b710fd 33a72a 0852e2 a3a793 7ec571
d7b43d 683193 e02373 3b412b; 1 km 34d0a5 8f5874. Judge outputs: `docs/review/land-zoom/round2/` (seams jsons, two
pictures, `table4.py` that prints the tables, `far_diag.py` the far-inside attribution).

## Follow-ups (drafts)
- `draft-land-zoom-held-ice-bed-before-final.md`: held ground under the neighbour's ice keeps its bed, which may lie
  below the sea; until `final()` the new section's own glacier must cover it or the vegetation's land test fails
  (not seen on these pairs; the lake case was).
- `draft-land-zoom-coast-switch-mid-ramp.md`: the coastline switches from the neighbour's to the section's own at the
  ramp's middle (+40 km): 3.6% coast mismatch at +40 on the coast seam; a coast jog where the two disagree.
