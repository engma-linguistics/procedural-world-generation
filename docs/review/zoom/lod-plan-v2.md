# Level-of-detail globe for v1.0, v2: scroll down from orbit, detail built on demand (build plan)

Lane 289, 2026-11-10. Supersedes the viewer flow of `lod-plan.md` (lane 282: click a section, double-click down rungs).
Tickets: PW-1673 (the viewer flow), epic PW-1198, PW-1299; PW-1296, PW-1355, PW-1359, PW-1341 (what happens to them: section 2.4).
Figures name their source; anything worked out here and not measured is marked *estimate*. The tile-size timings in section 1.3
were measured by this lane (marked "measured 11-10, lane 289").

## In plain words

Daniel 11-10: "as you optionally zoom into the world it would switch into the higher res view. A bit like zooming into google
earth", "I don't need zooms of every part of the world, nor do I like the idea of 'double click here to zoom'", and **everything
on demand**: nothing is pre-built; an area shows the blurry globe until its detail is built, then it sharpens and is kept.

**The scheme.** The planet is already cut into 54 big squares (the tiling's 4,000 km sections, 9 per cube face). Each square is
the root of a pyramid of tiles laid on that square's own flat map, every level 4x (the last 10x) sharper than the one above:

| Level | Sharpness | Tile | Tiles per big square | Made from | First build of one tile |
|---|---|---|---|---|---|
| 0 | the globe's cells (~21 km apart at L7, *estimate*) | | | the world | already there |
| 1 | 4 km per pixel | the whole 4,000 km square (1,000 px) | 1 | the world (today's section build) | 1 min 40 s, 5.7 GB (measured) |
| 2 | 1 km | 500 km (500 px) | up to 64 | level 1, by the fine pass | 17 s, 3.4 GB (measured) |
| 3 | 250 m | 125 km (500 px) | up to 1,024 | level 2 | 13 s, 3.5 GB (measured) |
| 4 | 25 m | 12.5 km (500 px) | up to 102,400 | level 3 | ~15 s (*estimate*, 1.3) |

As you scroll down, the viewer asks the server for the tiles on screen at the level your height calls for. The server builds
them one to three at a time, centre of the screen first, and forgets the ones you have scrolled away from; meanwhile you see
the level above, stretched. A built tile is kept on disk and shows instantly next time. Only what you look at is ever built.
The first time down over a new big square, it takes ~1.5-2 min before anything sharpens (level 1); after that, each level's
middle of the screen is sharp within ~15-20 s of reaching it and the whole screen within ~1.5-3 min (6-12 tiles a screen,
*estimate* from the measured tile times; about half that with two building at once).

**What has to change in the generator** so tiles built at different times meet without a seam: every tile of a level sits on
one shared pixel grid (the big square's map), reads its parent level as one stitched picture, and fades at its edge to a
surface that depends only on the place (the parent's ground plus place-keyed detail), not on the tile. Rivers follow courses
fixed by the parent, with their bends keyed to the river, not to the tile. Where two big squares meet, the later one is built
matched to the earlier (code that exists, `match.py`).

**Schedule.** Six build steps, about 10 lane-days; with two lanes the longest chain is about 7 lane-days, so it fits before
1 Dec (21 days away) with room for Daniel to judge and one fix round, *if* no step needs a second attempt. Questions for Daniel
are at the end (what level 1 should be, what happens at the big squares' edges, and the cut if it runs late).

## 1. The tile scheme

### 1.1 Where the tiles live

- **Big squares (cells).** `planet/zoom/tiling.py`: 6 faces x 3 x 3 = 54 cells for 4,000 km sections (`api.SECTION_KM`), each
  with its own `Frame(lat, lon, up)` (azimuthal equidistant, turned to the face's v axis). A cell lies wholly inside its 4,000 km
  square with at least 97 km to spare (`tiling.md`). The pixel scale of that map is within ~2% of true at the square's edge
  midpoints and ~3% at its corners (*estimate*: sin(rho)/rho at 2,000 and 2,830 km).
- **One plane, one lattice per level.** Every tile under a cell is an axis-aligned square on the cell's plane. Level k has a
  resolution r_k and a tile side T_k; pixel centres are at x = -2000 + (i + 0.5) r_k km (same for y), so all tiles of a level
  share one pixel grid, and a level-k tile is exactly n_k x n_k level-(k+1) tiles (level 1 holds 8 x 8 level-2 tiles, then
  4 x 4, then 10 x 10). Address:
  `(world, cell, level, tx, ty)`, tx, ty counted from the square's west and north edges. The tile's 3D position of any pixel
  is `cell_frame.to_sphere(x, y)`, so the viewer and the generator agree exactly.
- **Which tiles exist.** Only tiles within 8 of their own pixels of the cell's own area (the cell polygon, `tiling._boundary`,
  in its plane) are ever asked for (`lod.exists`); the rest of the square belongs to neighbouring cells and is drawn from
  there. The 8 px pad means every parent pixel a child inside the cell reads is in an existing parent tile. On `px.1.1` all 64
  level-2 tiles exist, on the corner-of-face cell `pz.0.0` 44 of 64 (computed by `lod.py`).
- **Level 1 is today's section.** The regional pass from the world (`regional.zoom(section=...)`, `POST /api/zoom
  {world, section, res_km}`, lane 283). It is the only level built from the world; everything below is the fine pass
  (`fine.build`) from the level above, so siblings share an ancestor and agree by construction (section 2).

### 1.2 The ladder: why these levels

- **Tiles of 500 px.** Measured (1.3): a 500 px tile is ready in 13-17 s at 3.4-3.5 GB, a 1,000 px tile in 38-43 s at 7.3-8.9
  GB, a 250 px tile in 8.5 s at 2.1 GB. Per area of ground, 500 px tiles cost ~1.5x the compute of 1,000 px ones and 250 px ones
  ~3.2x (the fixed part of a build is ~5 s). 500 px gets the middle of the screen sharp in seconds, lets two or three build side
  by side within the memory and core caps, and wastes less when you pan away; on-demand building can afford the 1.5x. A
  screen at the matching height holds ~6-12 tiles (*estimate*: a tile pixel drawn at 1-1.5 screen pixels on 1,920 x 1,080).
- **4x steps, last one 10x.** The measured rungs (`lod-rungs.md`) went 4x (2 km to 0.5 km) and 20x (0.5 km to 25 m); both looked
  right and agreed with the parent at the edge. 4x keeps the "stretched parent while building" view acceptable (a 4x blow-up);
  the last 10x saves a whole level of waiting at 25 m. 25 m stays the finest, as today (`fine.MAX_STEP` 20, `PARENT_RES` 0.1-4).
- **Level 1 at 4 km, not 2 km.** A 4,000 km section at 2 km takes ~4-5 min and 23.1 GB (`lod-plan.md`, `land-zoom/cost.md`);
  at 4 km it took 1 min 40 s and 5.7 GB alone on a busy machine (measured, 1.3). With on-demand building the first sharpening
  should be quick; level 2 brings the 1 km detail seconds later. The 4 km -> 1 km step (4x from a 4 km parent) was untried
  before this lane: it builds (1.3); how it looks is judged in step 1. This is question Q1.
- **When each level shows** (*estimate*, 1,080 px tall view, 40 degree field of view, a level is drawn when its pixel is under
  ~1.5 screen pixels): level 1 below ~4,000 km of height, level 2 below ~1,000 km, level 3 below ~250 km, level 4 below ~25 km.
  The globe's closest approach today is 1.15 radii (~950 km up, `globe/scene.js`); it goes down to ~50 m above the ground.

### 1.3 What a tile costs (measured 11-10, lane 289, unless marked)

Each tile build is `planet zoom <parent> --lat -4.0449 --lon 93.1529 --size-km S --res-km R` of world dba204, in a private data
root (read-only links to the world and to section 683193, cell `py.1.1` at 4 km), one at a time, `/usr/bin/time -v`, 8 threads
asked, on a busy machine (load 21-27 of 48 cores, 126-138 GB available). The spot is the section's roughest land block (relief
std 1.3 km). Level 1 is `planet zoom dba204 --section px.1.1 --res-km 4` (30% land).

| Build | Parent | Tile | Px | Wall | Peak RAM | CPU | Disk |
|---|---|---|---|---|---|---|---|
| level 1 | world dba204 | section `px.1.1` at 4 km | 1,000 | 100.4 s | 5.7 GB | 482% | 126 MB |
| level 2 | 683193 (4 km) | 250 km at 1 km | 250 | 8.5 s | 2.1 GB | 209% | 8.4 MB |
| level 2 | 683193 | 500 km at 1 km | 500 | 16.6 s | 3.4 GB | 230% | 33 MB |
| level 2 | 683193 | 1,000 km at 1 km | 1,000 | 42.7 s | 7.3 GB | 263% | 129 MB |
| level 3 | 74ff0c (the 1,000 km one) | 125 km at 250 m | 500 | 13.2 s | 3.5 GB | 270% | 33 MB |
| level 3 | 74ff0c | 250 km at 250 m | 1,000 | 37.9 s | 8.9 GB | 310% | 128 MB |
| level 4 (`lod-rungs.md`) | 0.5 km rungs | 30 km at 25 m | 1,200 | 36-42 s | 8.0-12.2 GB | 254-308% | 124-128 MB |

The first build in a fresh environment took 28 s for the 250 px tile (numba compiling; not counted). Level 4 at 500 px from a
250 m parent is not measured: from the level-3 rows and the 1,200 px rung, ~13-17 s and ~3.5-4 GB (*estimate*). These are
today's fine pass and today's centred frames; step 1's changes (shared lattice, stitched parent) should not change the cost
much (*estimate*), and step 1 re-measures.

Disk: 33 MB per 500 px tile with all 73 layers. A dive to 25 m at one spot (~6-12 tiles a level at levels 2-4, *estimate*) is
~1 GB; a whole cell at level 2 (64 tiles) ~2.1 GB.

## 2. Seams between tiles built at different times

### 2.1 What agrees today, and what does not

- **Child against parent: agrees.** The fine pass keeps each parent pixel's mean and fades back to the parent's surface at its
  edge (3D seam 0.4 m mean, 6 m max, overview §2.15; edge mean within +-2 m on the rungs, `lod-rungs.md`).
- **Place-keyed already:** the detail noise, ridges, the coast's fractal shore, the categorical warp and the rivers' wander are
  `ZK.fbm` at 3D planet positions with the build's seed (`fine.build`, `Pk`), so two tiles with the same seed draw the same
  noise where they overlap. Meander phase is keyed to the parent river's head (`fine._river_phase`).
- **Tile-keyed today (what breaks between siblings):**
  1. *The pixel grid.* `fine.build` makes `Frame(lat, lon, up=parent up)` centred on each tile: two siblings' pixels are on
     different maps (slightly turned and scaled against each other), so their edges cannot match pixel for pixel.
  2. *The fade at the edge.* Within `max(rp, 8 res)` of the edge (`w_in`), the result is blended back to `target`, the parent's
     bare bicubic surface with no detail. Two siblings both meet that surface at their shared edge, so heights agree, but each
     side shows a strip with no detail and no erosion: 8-10 px wide (a grid of smooth stripes in mountains, *estimate* from the
     ramp formula).
  3. *The parent window.* A tile near its parent tile's edge needs parent pixels from the parent's neighbour
     (`fine.check`: 3 parent px of margin plus a halo); today the parent is one zoom.
  4. *River courses and phases near the edge.* Courses are found on the parent window's network (`_courses`); a river whose
     head lies outside the window starts its phase at the window edge, so the meanders on the two sides of an edge are out of
     step. Small streams the fine pass finds by itself (draining less than `RIVER_AREA_PX` = 25 parent px) leave by the edge
     ring and restart on the other side.
  5. *Discharge.* Each tile accumulates its own runoff on top of the parent's inflow (`q_in`), so a river leaving tile A
     carries A's sum and enters tile B with the parent's number: close, not equal.

### 2.2 What changes in `planet/zoom/` (step 1)

1. **Tile frames** (new `planet/zoom/lod.py`): the level table, tile addressing, each tile's rectangle and pixel lattice on its
   cell's plane, parents, children, the tiles covering a rectangle; `Frame` gains a plane origin (`Frame.offset(x0, y0)` or the
   tile builds `px, py` on the shared lattice and keeps the cell's `Frame`), so siblings' pixels are one grid (fixes 1).
2. **A stitched parent** (`lod.parent_mosaic`): a tile's parent is the window of its parent level covering the tile, its halo and
   the bicubic's reach (3 + 1 + 2 parent px), cut from the parent-level tiles it overlaps (1, 2 or 4) into one raster on the
   shared lattice, with the meta `fine.build` reads (`_Parent`). Children on both sides of a parent-tile edge then read the same
   parent data (fixes 3). The cost: a tile near its parent's edge waits for the neighbouring parent tile; the queue builds it
   first (it is nearly always on screen anyway).
3. **Fade to a place-keyed surface:** the edge blends to `target + w_detail * amp * noise` (the detailed surface before the
   landscape pass: parent bicubic plus the place-keyed noise and ridges; `amp` from the parent's relief and rock, both local)
   instead of the bare `target`. Both siblings still reach the same heights at the shared edge, but the strip keeps its texture;
   only the landscape pass's carving fades out. The ramp can then shrink to ~6-8 px (fixes 2). The edge still meets the parent's
   mean, as today.
4. **Rivers fixed by the parent level:** a new layer `river_phase` (the meander phase at each river pixel) is saved by every
   tile and read from the parent, so phases continue across tiles and levels (as `gorge_path` already does for falls); the
   course of a parent river is smoothed over the mosaic, which extends beyond the tile by the halo, so the smoothing is the same
   on both sides. The imposed-river threshold drops for tiles (e.g. 4 parent px) so every stream wide enough to see at the
   tile's scale is the parent's, keyed by place; only streams below that may end at a tile edge (fixes 4).
5. **Discharge anchored to the parent:** along an imposed course, discharge is the parent's discharge at that point
   (bilinear along the course) plus the tile's own small tributaries joining it, not A's running sum; the two sides of an edge
   then carry the same number (fixes 5).
6. **Ids and determinism:** a tile's id is from `(world, cell, level, tx, ty, seed)`; rebuilding a deleted tile gives the same
   arrays (tested), so the cache can drop tiles and rebuild them. Level-1 sections matched to a neighbour depend on build order
   and are never dropped (2.3).

Done when (step 1): two sibling level-2 tiles of one section, built in either order, meet at their shared edge with a height
step across the edge no larger than the step between neighbouring pixels inside them (same distribution within 10%), every
river over the imposed threshold crosses the edge at the same place with the same discharge (within 5%), and a rebuilt tile is
bit-identical.

### 2.3 Between big squares (cells)

Two level-1 sections are independent landscapes built from the world: in their overlap they differ by tens of metres on plains
and hundreds in mountains (`match.py` docstring, `seams-round1.md`). The tiling already handles this: a section built while a
neighbour exists is built **matched** (`match.py`: the neighbour's ground where the neighbour owns it, exact at the owner line,
which for tiling sections is the cell edge, blended over 80 km inside; ~10% more time, `lod-plan.md`). On demand this means: when
level 1 of a cell is built, it is matched to whichever neighbours are already built. The viewer draws each cell's tiles only
inside the cell (the owner line), so the line is the seam, and there the two agree exactly at level 1; below level 1 both sides'
tiles fade to their own parent at the line, which agree (*estimate* that the residual is a few metres; measured in step 3).

Rivers across a cell edge: a river from the earlier cell into the later keeps its water (PW-1302, done); one from the later into
the earlier keeps the earlier cell's own estimate (PW-1355: off by >25% on the practice pairs). Order-dependence is the price of
not building the whole planet up front.

### 2.4 What happens to the old tickets

- **PW-1296 (the sweep):** not needed. On demand builds what is looked at; there is no planet-wide pass. Stays `later` (a
  pre-build of a showcase world's level 1 overnight remains possible with the same code, one at a time).
- **PW-1355 (mosaic discharge):** shrinks from "after the sweep" to a pairwise fix: when a cell is built next to an earlier one,
  correct the earlier cell's discharge for rivers coming in, then drop the earlier cell's cached child tiles that those rivers
  touch (they rebuild on the next visit). Not in v1.0 (Q2); stays `later`.
- **PW-1359 (side-by-side sections):** done by design when the globe draws every built cell's tiles at once (step 4); close it
  then.
- **PW-1341 (fine zooms in turned sections):** the generation half is done (`fine.build` already takes the parent's `up`);
  the 2D viewer half does not arise on the globe (tiles are placed on the sphere by their cell's frame). Close when step 4 lands.

## 3. On-demand serving

- **What the viewer sends.** `POST /api/tiles/want {world, gen, tiles: [[cell, level, tx, ty], ...]}`, the tiles the view needs
  that it does not have, in priority order, sent when the camera settles (~250 ms after it stops, and every ~2 s while moving).
  The server **replaces** its queue for that world with this list: anything no longer wanted is dropped, which is the
  cancel-on-pan. A build already running is not killed (it is under ~1 min and is kept). Each tile's ancestors that are missing
  (and the parent-level neighbours its mosaic needs) are added ahead of it.
- **Priority:** coarser levels first (a tile cannot be built before its parent), then distance of the tile's centre from the
  screen centre, then distance from the camera.
- **Workers and memory:** level-1 sections are heavy (one at a time, the existing `zoom_is_heavy` rule and `zoom_estimate`
  RAM check; 5.7 GB and ~5 cores measured at 4 km). Tiles of levels 2-4 are fine passes at 500 px (~3.5 GB and 2-3 cores each,
  measured 1.3): up to three at once while free memory stays over their peaks plus the 8 GB spare (`ZOOM_RAM_SPARE_GB`) and
  within the lane's core cap; one at a time when the machine is busy. The tile queue uses one of the server's 4 job workers; other jobs are unchanged. `zoom_peak_gb` gets fine-pass
  anchors from section 1.3 instead of the regional ones.
- **What the server returns.** `GET /api/tiles/status?world=&gen=`: per wanted tile, built / queued (position) / building
  (progress) / failed (message). Built tiles are fetched as `GET /api/tiles/<world>/<cell>/<level>/<tx>/<ty>/<file>`: `view.bin`
  (elevation as float16 and a water mask, ~2-3 MB, gzip on the wire), `satellite.png`, and any layer by name (the zoom layer
  files, so the existing layer code serves them).
- **The cache on disk.** Tiles are ordinary zoom directories (so `zoom.load`, the zoom page and the tests work on them) under
  `zooms/`, with a `tile` block in `zoom.json` and an index per world (`lod.tile_id`). Size (1.3): 33 MB per tile; a dive ~1 GB
  (*estimate*); Daniel exploring 50 places ~50 GB. A cap (default 60 GB, a setting) drops least-recently-viewed tiles of levels 2-4 when
  passed; level 1 is never dropped (matched builds depend on order; ~127 MB per cell at 4 km, ~6 GB for a world's 47 land
  cells). Deleting a world deletes its tiles (`planet delete`).
- **Owner-facing:** a small "building detail: 3 tiles queued" badge on the globe; nothing to click.

## 4. The viewer

- **One page.** The globe page (`viewer/index.html`, `viewer/globe/`) draws the tiles itself; no hand-over to `zoom.html`
  (which stays as the 2D map and analysis page, linked from a tile's info box).
- **Camera** (Google-Earth-like): wheel zooms toward the point under the cursor; the minimum height follows the ground under the
  camera (today's fixed 1.15 radii goes); rotation speed scales with height; below ~200 km the camera tilts toward the horizon
  as it descends (it can always be tilted back up). The near and far planes follow the height (`scene.js` already sets them per
  frame), with a logarithmic depth buffer below ~50 km (`?logdepth=1` exists; flagged as a shimmer risk on Daniel's Chrome,
  PW-415, so tested there first). Precision: a tile's vertices are stored relative to the tile's centre and the tile is placed
  by its own matrix, so float32 is exact to ~1 cm near the camera (*estimate*).
- **Choosing tiles** each time the camera moves: per cell in view (frustum and horizon test on the cell's corners), walk down the
  quadtree; refine a tile when its pixel would cover more than ~1.5 screen pixels. Wanted-but-missing tiles go to the server
  (section 3); what is drawn is the finest built tile at each place.
- **Fallback while building:** a tile's children that are built draw over it; the rest of its area shows the tile itself
  (stretched). The globe's own cells are level 0 and always drawn underneath. A child appears by fading in over ~0.4 s (alpha
  dithering, no transparency sorting). Edges between a coarse and a fine tile hide a crack with short skirts (a strip hanging
  down from each tile's edge).
- **Drawing a tile:** one shared grid mesh (e.g. 126 x 126 vertices, every 4th pixel; all of them close up) displaced in the vertex shader from
  the tile's elevation texture, placed on the sphere through the cell's frame (the formula in `zoom3d_place.js::aeFrame`);
  colour from the satellite image or the active layer, hillshade from the elevation; a fragment outside the cell is dropped
  (the owner line). Vertical exaggeration as on the globe, easing to 1x below ~50 km (*judgement*, to try).
- **Memory budget in the browser** (*estimate*): per 500 px tile ~0.5 MB elevation (float16), ~1 MB satellite (RGBA), ~0.25-1 MB
  for an active layer; ~3 MB with GPU copies. On screen there are ~10-40 tiles across the levels drawn; keep a
  least-recently-drawn pool of ~300 tiles (~1 GB), freeing GPU and JS copies beyond it. Measured with `tools/viewer_perf_globe.py`.
- **Layers follow you down:** the globe's layer menu maps each world layer to its zoom layer where one exists (elevation, rain,
  temperature, biome, soils, vegetation, rivers and so on; the zoom's 73 are listed in `fine-layers.md` and `zoom.json`); tiles
  fetch only the active layer (lazily, per tile, and keep it with the tile) and colour it with the same ramps and legends
  (`ramps.js`). A globe layer with no zoom twin shows the satellite view on tiles with a one-line note. Hover and click read the
  tile's value at the point (the active layer, else its elevation; the full readout loads that one tile's layers on click).
  Overlays drawn as lines on the globe (rivers, borders, settlements) keep drawing over the tiles; their finer versions on tiles
  (the tile's own rivers) come from the tile's layers.

## 5. Build steps

Each is about 1-2 lane-days. **Run first: steps 1 and 4 side by side (4 starts on level 1, which the API builds today). Then
2 and 3 side by side (2 needs step 1's tile addressing, which step 1 commits first). Then 5, then 6.**

| # | Step | Area | Lane-days | After | Done when |
|---|---|---|---|---|---|
| 1 | Tile scheme and seam-true fine pass | zoom | 2 | | `lod.py` (levels, addresses, lattices, parents, which tiles exist, parent sources: **done by lane 289**) plus the stitched parent; `fine.build` builds a tile on the shared lattice from a mosaic parent, fades to the place-keyed surface, carries `river_phase`, anchors discharge. Two sibling level-2 tiles built in either order meet at the edge with the step distribution of their interior (within 10%), rivers carried at the same place and discharge (within 5%), rebuild bit-identical; times and peaks per level measured; `pytest` passes. |
| 2 | Tile service | server | 1.5 | 1's addressing | `POST /api/tiles/want` (replace-queue, ancestors added, coarse-first then centre), status, tile files, one heavy at a time and the RAM check with fine anchors, the disk index and cap. A scripted client panning across a cell gets the centre tiles first, a pan away drops the rest of the queue, a second visit serves each tile from disk in under 100 ms; tests on a scratch data root. |
| 3 | Level 1 on demand, matched | zoom | 1 | | A cell's section is built at 4 km matched to built neighbours (match.py through the API); time and peak alone measured; two neighbours built in either order meet at the cell edge (heights within a few metres at the line, rivers carried); same for their level-2 tiles at the line. |
| 4 | Globe to the ground, levels 0-2 | viewer | 2 | (1 for level 2) | The globe camera goes from orbit to ~1 km above ground with zoom-to-cursor and tilt; level-1 and level-2 tiles drawn on the sphere with fallback, fade, skirts and clipping at the cell edge. Daniel can scroll from orbit to 1 km detail on a showcase world with tiles appearing and no camera jump (screen recording), 30+ fps. |
| 5 | Down to 25 m, layers on tiles | viewer | 2 | 2, 4 | Levels 3-4 drawn; the active layer and its legend on tiles; hover readout; browser memory pool. At three spots (mountain, coast, river plain) a dive from orbit to 25 m works end to end on the live server; renderer memory under ~1.5 GB after a 10-minute flight. |
| 6 | Judge and fix | all | 1.5 | 5 | Seams measured on the tiles Daniel's dives built (siblings, levels, cells); Daniel's look; one fix round. |

**Total: ~10 lane-days; longest chain 1 -> 2 -> 5 -> 6 = 7 lane-days, plus 4 alongside.** With two lanes from 11-11 that is
about 7-8 working days (*estimate*), done around 11-20, leaving ~10 days before 1 Dec for a second attempt at whichever step
fails. It fits **if** steps 1 and 4 land in one pass each: they carry the unknowns (seams; the camera and depth precision at
the ground on Daniel's Chrome). If either needs a second pass (three-strikes rule), the 25 m level is the part to defer (Q3).

## 6. Risks

- **Waiting.** A screen at a new level needs ~6-12 tiles of 13-17 s (1.3): the centre is sharp in seconds, the edges follow
  over 1.5-3 min (less with two or three at once). The first level-1 build of a big square is the longest wait (~1 min 40 s
  measured, ~10% more when matched). GPU work (PW-1198's v3) is the real cure, not v1.0.
- **Memory on a shared machine.** One tile build is ~3.5 GB, a level-1 section ~6 GB (1.3); the server's RAM check refuses with a message rather than
  build into a squeeze (daytime cap ~90 GB for all lanes).
- **Seams that numbers pass and eyes catch:** the fade strip (2.2 item 3) and level changes; step 6 is for this.
- **Depth and jitter at the ground:** a float32 globe of radius 1 has ~0.4 m steps at the surface (*estimate*); tiles relative
  to their centre and a moving near plane are the standard cure; logarithmic depth had a shimmer report (PW-415).
- **Disk:** ~0.15 GB per tile; the cap keeps it bounded.

## Questions for Daniel

**Q1. How sharp is the first step down from the globe?** When you scroll below ~4,000 km, the 4,000 km square under you is built
first; everything finer is built from it.
- A. 4 km per pixel: ready in under 2 minutes (1 min 40 s measured on a busy machine; 6 GB while building), then 1 km tiles
  sharpen the middle of the screen ~15 s later. (lean)
- B. 2 km per pixel: ~4-5 minutes before anything sharpens, 23 GB while building; the next level (0.5 km) is a little better.
- Lean **A**: on demand, a fast first sharpening matters more than the middle step.

**Q2. Where two big squares meet, how careful should the join be?**
- A. Match each square to its already-built neighbours (existing code, ~10% slower): the ground meets exactly at the line;
  rivers flowing into a square built earlier keep that square's own (rougher) idea of how much water they carry, so a river can
  change width at the line. (lean)
- B. A and also fix those rivers' water and rebuild the affected finer tiles (PW-1355 in its pairwise form): ~1.5 lane-days more,
  after the tag.
- C. No matching; blend the two squares' pictures over ~100 km: quickest, but in mountains you can see a ridge or river doubled
  in the blend.
- Lean **A for 1.0, B after the tag**.

**Q3. If it runs late, what is cut for 1.0?**
- A. Stop at 250 m for 1.0 (levels 1-3); 25 m right after the tag. The globe-to-ground feel is all there; only the last close-up
  waits. (lean, if a cut is needed)
- B. Stop at 1 km for 1.0 (levels 1-2): safest, but "down to the ground" stops at a regional view.
- C. Keep 25 m and drop layers on tiles for 1.0 (satellite view only below the globe; the layer still shows on the globe).
- Lean **A**; no cut planned unless step 1 or 4 needs a second attempt.

## State (handoff, lane 289, 11-10)

- Done: this plan; the tile timings in 1.3; `planet/zoom/lod.py` (the ladder, tile keys, rectangles and the shared pixel
  lattice, parents and children, which tiles exist near a cell, the tiles covering a view, the parent tiles a build reads, tile
  ids) with `tests/test_zoom_lod.py`. Nothing builds a tile from `lod.py` yet and nothing else uses it.
- Next (step 1): `lod.parent_mosaic` (cut the parent window from `parent_sources` into one raster with a `_Parent`-shaped meta;
  level 2 reads the level-1 section directly); a tile mode in `fine.build` (pixels from `lod.lattice` in `lod.frame(cell)`
  instead of a centred Frame; `check` against the window); the fade to the place-keyed surface; `river_phase` saved and read;
  discharge anchored on imposed courses; then the sibling seam test of 2.2.
- Inbox drafts filed for steps 1-3 (`issue-tracking/inbox/draft-lod2-*.md`).
