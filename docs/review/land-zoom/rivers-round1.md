# Land zoom rivers across sections, round 1 (PW-1302; epic PW-1299)

Lane 129, 2026-11-02, after lanes 127/128 (`seams-round1.md`, `seams-round2.md`). World `dba204` (Earth-like B, L7).
Code: `planet/zoom/match.py` (`inflows`, `walls`, `basin_lakes`, the neighbours' networks in `sources`/`source_of`,
`_owner` at any points), hooks in `stage_rivers.py::coarse_rivers` and `stage_landscape.py::final_drainage`,
`regional.py` (ctx slots, `zoom_id`). Judge: `docs/review/land-zoom/rivers.py` (new); outputs and table printer in
`docs/review/land-zoom/rivers1/`. Test: `tests/test_zoom_match.py::test_matched_section_carries_the_neighbours_rivers_on`.

## In plain words

1. **Before: every river flowing from the first-built section into the matched one dried up at the line.** The
   matched section holds its neighbour's ground as an outlet (a drain), so water that the neighbour's river carried
   across the line vanished there, and the river in the new section started again from nothing. On lane 128's five
   practice pairs, 0 of 53 such crossings carried their water on (a 95,000 m3/s river on the block W pair arrived as 0).
2. **Now the neighbour's rivers hand their water on.** From the neighbour's saved drainage network (its `receiver`
   layer), every place where its water crosses the line into the new section's ground gives that water to the new
   section's pixel there, before the landscape pass (so the valley below is graded for a river that size). Of the 53
   crossings, 48 now carry on within a factor of 2, and 22 of the 23 big ones (>= 500 m3/s; the one left is on the
   tile pair) within 25%. The course: the new section's river is within one pixel (2.5-4 km at 4 km/px, median) of where
   the neighbour's crosses.
3. **And the new section's water crosses into the neighbour's ground only where the neighbour has a stream coming in.**
   The first try (hand-on only) let a handed-on river run straight back out into the neighbour's ground at the next
   pixel (block W: 95,000 m3/s in, 104,000 out beside it). Now the neighbour's ground beside the line is a wall to the
   new section's water except where the neighbour's own network has a stream (>= 10 m3/s) entering from this side.
4. **Lakes still agree at the line** (lane 128's rule). A basin on the ramp that filled with a handed-on river made a
   lake reaching the line on the ice range pair (6 of 402 line pixels); the basin lakes now keep to the neighbour's
   lake outline there too, back to 0.
5. **Left: rivers flowing the other way, into the section built first.** That section was finished first, so its
   river below the line carries its own guess of the water from the other side; the new section can't change it.
   Big rivers agree within 25% at 30-67% of these crossings (tile: 19,200 m3/s delivered where the first section
   carries 3,900). The fix is a discharge-only pass over the whole mosaic after the sweep (draft below), which also
   handles a river crossing several sections or the same line twice.
6. **Heights at the line still meet** (median 0.0 m on all five pairs; p95 0.0-3.1 m, was 0.0-0.3: the line pixel's
   weight is 0.998, not 1, and the section's own valley under a handed-on river is deeper now). Zooms built without
   `--match` are unchanged (all new code runs only with a match; the golden and zoom tests pass unchanged); matched
   zooms get new ids (`zoom_id` adds `|rivers`), so lane 128's matched zooms, cited in seams-round2.md, stay as they were.

## Diagnosis (lane 128's matched pairs, before any change)

`rivers.py A B` (A built first, B matched to it). A river crossing the owner line is found in the upstream owner's own
network: a pixel it owns whose receiver the other owns, >= 50 m3/s; side-by-side pixels of one river within 12 km are
one crossing. Its counterpart: the downstream owner's river on its own ground within 12 km, flowing away from the line
(not a river of its own running into it), the nearest pixel carrying at least half the crossing's water (else the
largest discharge there).

- **A->B (into the matched section): broken everywhere.** Held ground is an outlet of the landscape pass and of the
  final drainage (`match.hold_edge`), so no water passes from it into B's own pixels; and B's coarse-river inflow, put
  in at its square's edge, lands on held ground too and is lost. q down / q up: desert 54 -> 0, range 252 -> 1,
  coast 7,139 -> 4, block W 129,619 -> 272, tile 16,176 -> 6,897 (the tile's 6,897 is B's own rivers nearby, not A's).
  The courses were right (B's ground at the line is A's, so B's valley carries on from A's) but dry.
- **B->A (into the section built first): partly right.** B's rivers drain into held ground wherever they reach it
  (every held pixel is an outlet); half of them meet one of A's rivers within 12 km (block W 19 of 36, tile 11 of 14,
  course within 2 km), at A's own discharge, within 25% for 20-29% of the big ones.
- **Lakes**: at the line they agreed already (lane 128), but for block W's 1-pixel fragment.

## Candidates

1. **Hand on the neighbour's crossing rivers as inflow** (taken). Exact on the neighbour's own network (its receivers
   are saved), cheap (one pass over its pixels), before the landscape pass so the valley is graded for the river.
   Alternative considered: the coarse rivers' inflow points (`ctx.inflow_pts`, `coarse_rivers`) moved to the owner line
   - only the coarse network's big rivers, at coarse positions, not the neighbour's own courses; rejected.
2. **Courses at the line**: pin B's receivers in the outer ramp to A's (mapped across lattices), or make held ground a
   wall except where A has a stream coming in (taken, final drainage only; the landscape pass still grades B's valleys
   down to A's levels everywhere, which is what keeps the heights meeting). Pinning was not needed: at the line B's
   ground is A's, so B's routing follows A's valleys once it can't drain sideways into held ground.
3. **Rivers crossing several sections, both ways.** A sweep order cannot help: rivers cross a line both ways and
   sections form loops. A planet-wide coarse discharge routing both sides read only fixes the coarse rivers' share.
   What works is a discharge-only pass over the finished mosaic (each owner's network on its own ground, joined at
   the crossings, accumulated once): exact for any number of crossings, no landscape pass. Drafted
   (`draft-land-zoom-mosaic-discharge-pass.md`); it needs the sweep's saved sections (PW-1296).

Tries, all kept (each was a refinement of the one before, not a failed approach): (1) hand-on only: most A->B rivers
carried on, but block W handed 95,000 m3/s in and B ran 104,000 back out beside it; (2) walls everywhere but
at A's incoming crossings of any size: B's rivers then left at A's hillside trickles (desert 166 m3/s into 0); (3)
walls but at A's incoming streams >= 10 m3/s (`ACCEPT_M3S`); (4) basin lakes kept to A's outline (the range's 6 px).

## The river seam table (4 km/px; before: lane 128's matched B; after: this lane's)

Pairs as seams-round2.md: A built alone, B matched to A. `python3 docs/review/land-zoom/rivers1/table.py docs/review/land-zoom/rivers1`.
Tolerance stated: a crossing is carried on when the counterpart is within a factor of 2, agrees when within 25%.

| pair | direction | build | crossings | carried on (x2) | within 25% | median abs log2 | big >= 500: n, within 25% | course offset km | total m3/s up -> down |
|---|---|---|---|---|---|---|---|---|---|
| desert | A->B | before | 1 | 0 | 0% | 15.72 | 0, -% | - | 54 -> 0 |
| desert | A->B | after | 1 | 1 | 100% | 0.00 | 0, -% | 4.1 | 54 -> 54 |
| desert | B->A | before | 1 | 0 | 0% | 16.08 | 0, -% | - | 69 -> 0 |
| desert | B->A | after | 0 | 0 | -% | - | 0, -% | - | 0 -> 0 |
| range | A->B | before | 4 | 0 | 0% | 11.97 | 0, -% | - | 252 -> 1 |
| range | A->B | after | 4 | 4 | 100% | 0.09 | 0, -% | 2.5 | 252 -> 272 |
| range | B->A | before | 3 | 0 | 0% | 15.88 | 0, -% | - | 213 -> 0 |
| range | B->A | after | 1 | 0 | 0% | 11.68 | 0, -% | - | 119 -> 0 |
| coast | A->B | before | 8 | 0 | 0% | 11.57 | 7, 0% | - | 7,139 -> 4 |
| coast | A->B | after | 8 | 8 | 100% | 0.00 | 7, 100% | 3.0 | 7,139 -> 7,146 |
| coast | B->A | before / after | 0 | - | - | - | - | - | - |
| blockW | A->B | before | 21 | 0 | 0% | 7.02 | 8, 0% | - | 129,619 -> 272 |
| blockW | A->B | after | 21 | 20 | 86% | 0.05 | 8, 100% | 3.6 | 129,619 -> 130,726 |
| blockW | B->A | before | 36 | 19 | 42% | 0.74 | 14, 29% | 1.9 | 136,890 -> 414,006 |
| blockW | B->A | after | 20 | 13 | 40% | 0.47 | 10, 30% | 1.9 | 258,652 -> 491,564 |
| tile | A->B | before | 19 | 3 | 0% | 5.33 | 8, 0% | 10.0 | 16,176 -> 6,897 |
| tile | A->B | after | 19 | 15 | 63% | 0.07 | 8, 88% | 3.7 | 16,176 -> 20,595 |
| tile | B->A | before | 14 | 11 | 43% | 0.35 | 5, 20% | 2.1 | 21,600 -> 16,478 |
| tile | B->A | after | 13 | 10 | 62% | 0.11 | 6, 67% | 2.0 | 30,300 -> 14,045 |

Read: A->B is fixed but for small rivers of the tile pair, where B's network joins a handed-on stream to a bigger
river within a pixel or two of the line (207 -> 3,555 m3/s; in A they are apart) or turns it back into A's ground (524 ->
0). B->A totals rise (block W 137k -> 259k up) because B now carries A's handed-on water and some of it re-crosses
into A where A's own river does too: that is the one-way limit of item 5. The desert's B->A crossing is gone: B's
166 m3/s river met the line where A has nothing coming in, and now turns away (draft below).

Lakes at the line (B's first own pixels, A sampled there): unchanged on all five (range 8/8 lake pixels, block W 1 px
A lake / B land, a fragment below the 3 px minimum, lane 128).

Heights (seams.py --owner, `rivers1/seam-<pair>-rivers.json`), line station median (p95) m: desert 0.0 (1.3), range
0.0 (3.1), coast 0.0 (0.0), block W 0.0 (0.1), tile 0.0 (0.5); coast at the line 0.00-0.11%, as lane 128.

## Zooms (4 km, kept, cited)

| pair | A (lane 116/128) | B matched, lane 128 (before) | B matched, this lane (after) |
|---|---|---|---|
| desert | d904d6 | a13667 | 5d2e02 http://localhost:8765/?world=dba204.json&tab=zoom&zoom=5d2e02 |
| ice range | fe600a | 59336f | e2313a http://localhost:8765/?world=dba204.json&tab=zoom&zoom=e2313a |
| coast | b710fd | 0852e2 | b9c5c8 http://localhost:8765/?world=dba204.json&tab=zoom&zoom=b9c5c8 |
| block W | a3a793 | d7b43d | 3580b7 http://localhost:8765/?world=dba204.json&tab=zoom&zoom=3580b7 |
| tile (py.1.1 / py.0.1) | 683193 | 3b412b | 83b0b1 http://localhost:8765/?world=dba204.json&tab=zoom&zoom=83b0b1 |

Each ~2.5 min, five at once. 1 km: ce39ed (below).

## The 1 km check

The tiling pair at 1 km/px (4000 x 4000 px): lane 128's `py.1.1` alone **34d0a5** as A; `py.0.1 --match 34d0a5`
rebuilt with this lane's code, **ce39ed** (22 min 42 s, peak 107.6 GB; 1,480 crossings hand on 21,388 m3/s), against
lane 128's matched **8f5874** as before. Viewer: http://localhost:8765/?world=dba204.json&tab=zoom&zoom=ce39ed
(judge jsons `rivers1/rivers-tile1km-*.json`, `rivers1/seam-tile1km-rivers.json`).

| direction | build | crossings | carried on (x2) | within 25% | median abs log2 | big >= 500: n, within 25% | course offset km | total m3/s up -> down |
|---|---|---|---|---|---|---|---|---|
| A->B | before (8f5874) | 21 | 3 | 0% | 4.81 | 7, 0% | 5.8 | 15,926 -> 4,447 |
| A->B | after (ce39ed) | 21 | 20 | 90% | 0.01 | 7, 100% | 0.9 | 15,926 -> 16,021 |
| B->A | before | 17 | 14 | 65% | 0.17 | 6, 67% | 0.7 | 21,304 -> 25,029 |
| B->A | after | 18 | 14 | 56% | 0.19 | 8, 50% | 0.8 | 27,550 -> 21,828 |

Lakes at the line: none either side (3,974 line pixels). Heights at the line: median 0.0 m, p95 0.07 m; ramp +20 km
1.7 (17.8) m, +40 11.1 (118), +70 33.5 (358), as lane 128's 1.7 (16.5) / 11.5 (113) / 33.9 (359); coast at the line
0.00%, +40 km 0.37%. Same picture as at 4 km: rivers into the matched section are fixed, those into the first-built
section stay at the first section's own estimate (draft).

## Follow-ups (drafts)
- `draft-land-zoom-mosaic-discharge-pass.md`: one discharge pass over the whole mosaic after the sweep (rivers into the
  section built first; rivers crossing several sections).
- `draft-land-zoom-walls-divert-rivers.md`: the later section's rivers that reach the line where the earlier one has
  nothing coming in now turn away; look at them, and `ACCEPT_M3S` (10 m3/s) at 1 km/px.
