# Level-of-detail globe, step 6: judge and fix (lane 306, 11-11)

PW-1673, `lod-plan-v2.md` §5 step 6. World dba204 copied (not linked) into a fresh scratch data root, nothing built.
Own server (`planet serve --port 8806 --jobs 4 --threads 2`, 8 cores) under `systemd-run --scope -p MemoryMax=24G
-p MemorySwapMax=0`; headless Chrome on the GPU, 1,600 x 1,000, `tools/viewer_lod_dive.py ... --cursor=0.5,0.5 --embed
--wait=900 --settle=240 --nadir` (new: `--settle` waits for the view's tiles at the 1 km, 250 m and 25 m marks, `--nadir`
shoots the same place straight down). Spots: **border** 5.5, 72.886 (on the py.0.1 / py.1.1 line, high mountains,
cold cache), **corner** -16.3, 72.95 (where py.0.0, py.0.1, py.1.0, py.1.1 meet; level 1 of py.0.1 and py.1.1 already
built by the first dive, the two southern cells cold), and the border again after the fix (cache warm). Seams measured on
the tiles these dives built (8 level-1 sections, 36 / 44 / 61 tiles of levels 2 / 3 / 4) by the new
`tools/lod_judge_seams.py`. Screenshots, the three dive reports and the seam numbers: `lod-judge-306/`.
A coast spot was not dived (budget).

## Verdicts

| Item | Verdict | Numbers |
|---|---|---|
| Sibling seams (heights) | **Pass** | Against the same line with no seam (one block carved over both tiles, PW-1697's rule), 7 pairs at levels 2-4: score median 0.92-1.12, p90 0.97-1.02; 6 of 7 within 10% on the median, 7 of 7 on p90 (the miss: py.0.1/4/281/109 : 282/109, 0.916). All 168 built pairs against their own inside band: median ratio 0.98-1.16 a level, no cliff (largest step 860 m at level 2 in 4 km-relief mountains, where the inside band has the same). |
| Level seams (child against its parent stretched) | **Pass** | \|child - parent bilinear\| at the child's outermost pixels over the same 16-48 px inside: median ratio 1.02 / 1.01 / 0.97 (levels 2 / 3 / 4, 36 / 44 / 61 tiles), p90 1.05 / 1.01 / 0.95; worst tile 1.31 (median), 2.46 (p90, py.1.1/4/9/108). The edge is no worse than anywhere a child meets its parent. |
| Cell-edge seams (heights) | **Pass** | `line_seam` against the floor (`resampled`), 4 lines round the corner and the border line: score 0.91-1.02 (median), 0.99-1.01 (p90) at every level with more than 100 points; e.g. py.0.1 : py.1.1 level 4, 104 points, 0.13 / 0.78 / 5.1 m = the floor. |
| Cell edge on screen at 25 m | **Failed, fixed** | The tiles were clipped to their cell by a 2,048 px mask of the 4,000 km square (2 km texels, "generous"): at 25 m the two cells overlapped by up to ~1 km, far past the line's fade (~250 m), and their grounds cut through each other in a long straight wall (`border_20_ground_300m_before_fix.png`). Fixed: exact clip (below); after: one straight line, no wall (`after_17_ground_300m.png`, `after_15_25m_straight_down.png`). |
| Colours at a cell edge at 25 m | **Fails, drafted** | With the heights matched, the satellite colours are not: snow and alpine scrub patches end on the line (`after_15_25m_straight_down.png`). Sibling tiles' colours are fine (colour-step ratio across / inside median 1.01-1.12 a level, away from cell edges). |
| The look, 1 km | Good | `border_08` / `border_09`: sharp, rivers on the tiles continuous across the level-2 tiles. The level-1 to level-2 switch shifts the colours (greener level 1, greyer snowier level 2, `border_07`): noticed, not fixed. |
| The look, 250 m | Fair | `border_12` / `border_13`: rivers drawn as 250 m pixel staircases; straight lines where level-3 tiles meet the stretched level 2 while building; the colour line at the cell edge. |
| The look, 25 m | Fair after the fix | Snow and vegetation patches have polygonal outlines a few km across (the world's cells showing through the categorical layers, `border_18`, `corner_17`); at 300 m the 4-pixel mesh (100 m) shows as facets in the foreground (`after_17`). A level-4 tile arriving over its stretched parent stands up from it with a skirt wall until its neighbours come (`border_16`). |
| fps | **Pass** | Every moving frame at the 60 fps cap in all three dives (600-618 down, 233-294 out); a frame drawn back to back 0.5-1.0 ms at the ground (992-2,083 fps uncapped). |
| Camera jumps | **Pass** (one note) | Largest per-frame turn of the camera's position 0.014 degrees, of the view 0.504 (the tilt's rate). The height over the drawn ground changed by up to 1.39x in a frame low down (one wheel notch is 1.116): the ground itself moves up when finer tiles arrive under a ridge (e.g. 2.37 -> 1.92 km as 22 level-4 tiles came in): a pop, not a camera jump. |
| Build waits (cold cache) | **Slow at borders** | Border: first level 1 (py.0.1) drawn 334 s after the stop; the neighbour py.1.1's level 1 only after that (one level-1 build at a time, matched to the first), so half the screen stayed globe hexagons for minutes (`border_07`, `border_08`); level 2 then 28 s, level 3 at once (built meanwhile), level 4 114 s. Corner (two cells warm): level 2 38 s, level 4 104 s; the two cold southern cells stayed flat globe cells through the 250 m mark (`corner_10`). The settle wait (240 s) ran out at the 1 km and 250 m marks in both dives: a tilted screen wants 22-51 tiles. |
| The corner at the ground | **Unclear, drafted** | At 300 m over the corner, settled (nothing queued or building), the hover read "Detail 1 km/px" at the screen's centre and the ground looks 1 km blurry (`corner_19_ground_300m.png`). Not traced. |
| Tile cache cap | Not exercised | 6.1 GB of tiles after both dives (60 GB cap). Eviction order (finest first, never level 1 or what a build reads) is `tests/test_tiles.py`'s; not re-run against a small cap here. |
| Server memory under its cap | **Pass, tight** | The 24 GB scope peaked at 22.9 GB (memory.peak), 22.2 GB current at most: 14.7 GB anonymous (4 workers ~3.7 GB each after tile builds) + 6.2 GB page cache. The anonymous part is well under; the page cache is reclaimable. |
| Browser memory | Pass | Renderer 0.94-1.27 GB at the ground, tile data 174-258 MB. |

## The fix: tiles clipped to their cell exactly

`viewer/globe/lodtiles.js`: the fragment shader no longer reads a 2,048 px mask of the cell's outline. It works out
the cube cell of its own point on the sphere, as `tiling.locate` does: the face's normal A and tangents U, V, and the
cell's edges as face angles (`lodmath.js::cellAngles`, `inCellAngles`; `(pi/4) sign(t)|t|^0.88`). A fragment is drawn when
A.p > 0 and atan(U.p / A.p), atan(V.p / A.p) are within the cell's edges plus one pixel of the tile's level (the band
where both cells' tiles hold the line's ground: the fade weight is 1 within 1.5 px of the line, `lod_build.line_surface`).
The cell edges are great circles, the same for both cells, so the clip is exact to float32 (~0.4 m) at every level; the
masks (4 MB each on the GPU) are gone. `tests/test_viewer_lod.py::test_tile_clip_is_tiling_locate`: 1,500 random points
and 44 within ~6 m of an edge, a face edge or a corner: each in exactly one cell, `tiling.locate`'s.

Before / after at the border, 300 m up, tilted 75 degrees: `border_20_ground_300m_before_fix.png` (a wall running away
from the camera along the line) against `after_17_ground_300m.png` (one straight line; the colours still differ across it).

## Drafts (inbox)

- `draft-lod-satellite-colours-differ-at-cell-edges.md`: at 25 m the two cells' satellite colours (snow, scrub) end on
  the line though the ground matches.
- `draft-lod-cold-border-waits-for-level1-in-turn.md`: at a border or corner the cells' level 1 are built one after
  another (~5.5 min each with 2 threads), so part of the screen stays globe hexagons for 5-20 minutes.
- `draft-lod-corner-ground-stays-at-1km.md`: settled at 300 m over the corner, the centre reads and looks 1 km.

## Tools

- `tools/viewer_lod_dive.py`: `--settle=S` and `--nadir` (above).
- `tools/lod_judge_seams.py WORLD OUT.json [--carve=N]`: siblings (edge steps, the carved no-seam reference, colour
  steps), levels (child against its parent stretched) and cell lines (`line_seam` against `resampled`) over every tile in a
  data root's tile index.

## In plain words

I dived twice from orbit to 300 m over dba204 on a fresh copy, once on the line between two big squares in the
mountains and once where four big squares meet, the way you would, and measured the tiles those dives built. The
ground itself joins up: neighbouring tiles, a sharp tile beside its blurry parent, and the two sides of a big square's
edge all meet as well as the same ground with no join at all. It runs at 60 fps all the way down and the camera never
jumps. The one ugly thing I could fix: right at the ground on a square's edge, the two squares' tiles overlapped by up
to a kilometre and cut through each other in a long wall. Each tile is now trimmed exactly at the edge, and the wall is
gone. Still wrong, and written up for later: the colours (snow, scrub) change on that edge line even though the ground
matches; the first visit to a border is slow, because each square's first picture is built one after another (5-6
minutes each here, so half the screen can stay as blurry hexagons for several minutes); and at the four-square corner
the ground under the camera stayed at the 1 km detail.
