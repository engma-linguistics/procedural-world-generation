# Nested fine zoom (PW-129): a zoom of a zoom at 100–250 m/px, shown in the 3D view

Status: Python side built (2026-10-16, planet/zoom_fine.py; see "As built" at the end). The 3D tile is still to do.

## What the owner asked for

A more granular pass of the area round a point of interest (a waterfall, a valley), 25–50 km
across at 100–250 m/px, conditioned on the parent zoom's heights, rivers, falls, lakes and rock
the way zooms are conditioned on worlds, with falls, plunge pools and gorges resolved at that
scale, and tied into the 3D view.

## Recommendation in one paragraph

Build it as a **separate, smaller pass** (`planet/zoom_fine.py`) that takes a finished parent zoom
as its "coarse" input, not by feeding the parent's pixels through `zoom.build` as if they were
world cells. The parent has already decided the geology, the climate, the drainage and where every
fall and lake is; the fine pass only reshapes the ground below the parent's pixel scale (valley
walls, cliffs, gorges, plunge pools, talus, floodplains) and redraws what depends on that shape
(glacier outlines, vegetation, the satellite colours). It writes an ordinary zoom directory (same
layers, same `zoom.json` format plus a `parent_zoom` block), so the 2D viewer opens it unchanged,
and the 3D view draws it as a second `Tile` inset into the parent. ~10 s per fine zoom, ~18 MB on
disk.

## Why not reuse `zoom.build` on the parent's pixels

`build` is written for ~55 km cells on the sphere: it reads world cell arrays (`flow`/`downstream`,
`plate_boundary`, `sediment_cover`, landform classes, the volcano table, seasonal climate),
Gaussian-interpolates with sigma = half a cell, designs knickpoint staircases from coarse river
drops (`knickpoints`, `staircase`), lays deltas and volcanoes, and keeps each cell's mean in 12
smooth passes. Presenting 2,500 parent pixels as "cells" would mean faking most of those fields,
and it would redesign falls the parent already placed. Its constants (HALO_CELLS, MEAN_PASSES,
river thresholds, the stream-power law calibrated at 0.5–4 km/px) are also tuned for that scale.

## The fine pass, step by step

Input: parent zoom `P` (layers as `zoom.load`), the fine centre (lat, lon), `size_km` (25, 50 or
100) and `res_km` (0.1, 0.2 or 0.25); 500 px across as for zooms (50 km at 100 m, 125 km at 250 m;
the 25 km option is 250 px at 100 m). The region must lie inside the parent minus a margin of
`max(8, halo)` parent pixels (the parent's own halo is cropped off, so there is no ground beyond
its edge to condition on); the viewer greys out picks too close to the edge.

1. **Projection.** Azimuthal equidistant round the fine centre, as zooms (`Frame`); every fine
   pixel's position in the parent's frame is computed exactly (lat/lon -> parent projection), so
   sampling the parent is exact even 1000 km from the parent's centre.
2. **Target surface.** Parent `elevation` (ice surface included), bicubic in the parent's pixels;
   `ice`, `water`, `lake_depth`, `discharge`, `drainage_area`, climate layers bilinear;
   categorical layers (`rock`, `surface_rock`, `landform`, `climate`, `biome`) nearest after a
   noisy warp (as `zoom` does for cells). Plus detail noise at wavelengths from ~2 parent px down
   to ~4 fine px, sampled at 3D planet positions in km (so sibling fine zooms of one parent agree
   where they overlap), amplitude from the parent's local relief and rock ruggedness (`RUGGED`).
   Each parent pixel's mean is pulled back to the parent's height (the zoom's mean-keeping
   correction, a few passes at the parent-pixel scale).
3. **Imposed water.** The parent's rivers (its D8 receivers, rebuilt as `Tile.flow` does in
   zoom3d.js, or better stored by the parent zoom as a `receiver` layer: one more uint8 slot like
   the run's `nbr_slot`) become Catmull-Rom polylines through the parent pixel centres, noise-warped
   by < half a parent pixel; their discharge enters at the fine region's edge; channels are cut
   with widths from discharge (hydraulic geometry, w ~ 4 Q^0.5 m: 10 m3/s -> 13 m, 1000 -> 130 m:
   resolved at 100 m/px for the big rivers only, sub-pixel streams as now). Parent lakes become
   lakes at their surface, outlined where the target crosses it (shore detail from the noise).
4. **Falls, resolved.** Each parent fall in the region (`stats.falls`: lip pixel, `height_m`,
   `length_km`, `kind`, `discharge_m3s`) is laid out explicitly instead of being a chute over a
   few parent pixels: the lip at the parent's lip position on a resistant cap (rock from
   `surface_rock` / `lip_resistance`), a near-vertical face of the parent's full drop (one to a
   few fine px), a gorge downstream as long as the lip has retreated (`length_km` minus the face),
   as wide as 2–5 river widths, its walls held at the lip's level (hanging side valleys fall into
   it), and a plunge pool at the face's foot (depth ~0.1–0.3 x the drop, diameter ~1–3 x the
   river's width; PW-341's fix in the parent decides which pixel is the foot). Cascades and lake
   outlet rapids stay as steep reaches. Every fall listed in the fine zoom keeps the parent's id
   (`parent_fall: k`), so the viewer and highlights can match them.
5. **Landscape pass at the fine scale.** The zoom's steady-state stream-power loop (priority
   flood, D8, slope = C/K Q^-0.5, C refitted per parent pixel to keep its mean) with two changes
   that matter below ~250 m/px:
   - a **channel head**: pixels draining less than ~0.1–0.5 km2 are hillslopes, not channels, and
     sit at a threshold slope (~30–35 degrees, less on soft rock and under soil, more on hard
     caprock: cliffs), with creep rounding the tops; this is what makes valley walls and spurs
     look right at 100 m;
   - **talus**: the foot of every face steeper than ~45 degrees gets an apron at ~33 degrees.
   The imposed rivers, lakes and falls are held as in the zoom (receivers pinned along each
   reach, banks held above the river).
   The outer ring (a halo of ~2 parent px, cropped off afterwards, as PW-321) is held at the target
   so the edge meets the parent's surface: in the 3D view the seam needs no stitching beyond a
   one-pixel skirt.
6. **Glaciers, climate, life.** Ice outlines redrawn on the fine surface from the parent's ice
   thickness (bilinear) and the pixel's lapse-corrected climate (`icemass.balance` as `glaciers()`),
   tongues down the fine valleys; temperature lapse-corrected from the parent's to the fine
   height; vegetation per pixel (`zoom_vegetation`, ~4 s at 500x500 today), soils, wetlands; the
   satellite colours (`satellite.py`) as for zooms; landform overlays where they have a fine form
   (karst dolines, dunes) from the parent's `landform` class.

Outputs: `zooms/<id>/` as a zoom, `zoom.json` with `"parent_zoom": {"id", "offset_km": [x, y],
"rect_px": [r0, c0, r1, c1]}` (where it sits in the parent) and `source_world` copied from the
parent; the parent's `zoom.json` is not rewritten (the index lists children: `store.update_index`
groups by `parent_zoom.id`, as worlds list their zooms).

## Server and CLI

- `planet zoom <zoom_id> --lat --lon --size-km 50 --res-km 0.1` (a zoom id where a world is
  expected means a fine zoom; `zoom.zoom` dispatches to `zoom_fine.build`).
- `POST /api/zoom {zoom: <parent>, lat, lon, size_km, res_km}` in `api.zoom_job`: the same job
  machinery, lock and id scheme (`zoom_id(parent_id, ...)`); `parse_zoom_request` accepts `zoom`
  as a third source beside `run` and `world`.
- `planet delete` of a parent deletes its fine zooms (orphans, as zooms of a deleted world);
  `tools/cleanup_outputs.py` keeps a parent while a child is kept.
- A fine zoom of a fine zoom is not offered (the conditioning is designed for 0.5–4 km parents).

## Cost

| | today's zoom (500 px, 0.5–4 km) | fine zoom (500 px, 0.1–0.25 km) |
|---|---|---|
| conditioning | Gaussian interp of ~1000 cells, deltas, volcanoes, knickpoints: ~2 s | bicubic of ~2,500 parent px, falls laid out: < 1 s |
| landscape loop | ~15 iterations on (500 + 2 halo)^2: ~4–6 s | same loop, ~10 iterations (the parent fixes the network): ~3–4 s |
| glaciers, climate, vegetation, satellite | ~5 s | ~5 s |
| total | 10–15 s | ~8–10 s |
| disk | ~18 MB | ~18 MB |

One worker process per build, as zooms; nothing new in `api.COMPUTE`.

## The 3D view

`zoom3d.js` is already built for more than one terrain: `Tile` takes a centre offset, and picking,
ground heights and the camera ask the finest tile under a point (`Zoom3D.tileAt`). What's left:

- **Placing the tile.** The fine tile's vertices in the parent's scene frame (km): each fine pixel
  centre -> lat/lon (its own projection) -> parent projection, done once in JS (250k points). Its
  heights use the shared group scale (one exaggeration).
- **A hole in the parent.** The parent's mesh skips the quads inside the fine rect minus one fine
  pixel (an index rebuild, ~20 ms), the parent's sea shader discards inside the rect (a `uRect`
  uniform), and its fall ribbons and pins inside the rect are dropped in favour of the fine tile's.
  The fine tile's skirt hides sub-pixel cracks at the seam.
- **Per-tile data.** Each tile carries its own colour texture, data texture (heights, ice, sea,
  lakes: `zoom3d_look.dataTexture`), flow texture, lakes mesh, fall ribbons and sea plane, as the
  zoom's tile does today; the materials are cloned per tile (their uniforms differ). The colours:
  zoom.html's `renderLayer` draws the active layer of `state.meta`/`state.L` into `state.off`;
  it would take a (meta, L) pair so it can draw the fine zoom's layer too (the bulk of the
  zoom.html change).
- **Loading.** Opening a zoom lists its fine zooms (`zooms/index.json` children); the 3D panel
  gets "Fine zooms: on/off" and the list; `?id=<parent>&view=3d&fine=<child>` opens one.
  "Fine zoom here" (a button in the hover card, or shift-double-click on the ground) posts the
  job for the point under the cursor (50 km at 100 m by default, 25 / 100 km offered) and adds the
  tile when the job is done, flying the camera to it.
- **Detail on the GPU.** 500x500 at full detail is ~0.5 M triangles, the same as the parent: two
  tiles at full detail draw in ~1 ms at 1080p (measured 0.65 ms for one with the new effects).
  Far from the fine tile the parent alone is drawn at full detail; the fine tile could drop to half
  detail beyond ~3x its size (a `step` per tile; not needed for one or two fine tiles).
- **River flights** use `groundY`, which already asks the finest tile, so a flight down a parent
  river passes through the fine tile at its resolution: the gorge and the fall's face appear as
  the camera reaches them. The flight's course stays the parent's; inside the fine tile it could
  follow the fine river's pixels instead (the fine tile's `Tile.flow` gives them).
- **2D map.** The fine zoom's preview drawn over the parent at its rect (optional), and its own
  2D page as any zoom.

## Open questions for the owner

1. Sizes: 500 px across (50 km at 100 m, 125 km at 250 m), or the ticket's 25–50 km with fewer
   pixels? Lean: 500 px, 50 km at 100 m as the default, so a fine zoom costs and looks like a zoom.
2. Should a fine zoom also be offered straight from a world (a zoom at 100 m with the coarse
   pipeline)? Lean: no; the coarse pipeline's assumptions don't hold at 100 m, and the parent zoom
   is cheap to make first (the viewer can make both in one job).
3. Falls in the fine zoom: always exactly the parent's heights (lean), or re-derived from the fine
   terrain (more emergent, but a fall could then differ from the one the parent listed)?

## Owner decisions (2026-10-16)

1. **Sizes.** The finest view is ~25 km across, small enough for one volcano, waterfall, bay or
   reef. Build 500 px (25 km at 50 m/px) as the default and also try 1000 px (25 km at 25 m/px)
   to see what it buys; a 50 km view (500 px at 100 m) is also wanted.
2. **Progressive nesting, not from a world.** Fine zooms are made from an existing zoom, and
   further in from a fine zoom: world -> zoom (0.5-4 km/px) -> fine (50 km at 100 m) -> finer
   (25 km at 50 or 25 m). This replaces "a fine zoom of a fine zoom is not offered": each step is
   at most ~10-20x in resolution, so the conditioning stays honest (a 25 km box straight from a
   1 km/px zoom would invent almost everything from 25x25 parent pixels). The conditioning must
   therefore work for parents from 4 km down to 100 m/px.
3. **Fixed features keep the parent's values exactly**: fall heights (lip, face, plunge pool from
   the parent's drop) and volcanoes (summit height, crater/caldera, vents) at every level.

Cost at 1000 px: 4x the pixels, so ~30-40 s per build and ~70 MB on disk; ~2 M triangles in the
3D view (fine on this GPU). River flights through fine tiles: nice to have, not required.

**Trees.** At 50 m/px a pixel is a stand of trees and a canopy texture is right; at 25 m/px a
pixel is one to three crowns and a low 3D camera will show a smeared canopy. That is the
threshold where canopy height (forest 20-40 m tall vs the ground) and instanced tree sprites
start to pay off. Not in this ticket; warn the owner before the 25 m tier ships if it looks flat.

## As built (2026-10-16)

`planet/zoom_fine.py` follows steps 1-6, with these differences (each has an inbox draft where it's a judgement call or a gap):
- **Means over 3x3 parent pixels**, not per pixel: kept per pixel, a parent's 1-px canyon (170672) came back as a staircase of parent-pixel blocks. Block means are kept to 7-20 m rms, single pixels to 30-120 m.
- **Rivers**: parent links draining >= max(25 parent px, 1 km2) are imposed, warped by <= 0.5 parent px (none at a fall's lip). Beds fall all the way down, and the finished drainage is routed with the courses sunk, so water follows them. A river entering from outside gets the parent's discharge once, at its first node inside the region.
- **Falls**: lip = the parent's water surface at its lip; plunge pool surface = lip - height_m, both exact. The gorge runs along the parent's chain to its foot, walls falling from lip height by the face to the smoothed surroundings at the mouth. Ids are `parent_fall` plus a `lineage` back to the first zoom.
- **Volcanoes**: the cone's core (the parent's surface down to a 30% drop) is held, with a peaked shift so its top is the parent's top_m exactly. Out to its foot, the landscape pass stays within 30 m of the parent's cone.
- **Not redone**: glacier outlines, landform overlays, deltas and reef forms. These use the parent's, interpolated.
- **Cost**: 3.5-6 s and ~21 MB per 500 px, 18 s and 83 MB at 1000 px (25 m).

## Handoff (not yet done)

- 3D tile: the fine zoom as an inset Tile in zoom3d (separate agent).
- 2D page: a "fine zoom here" pick and the children's rectangles (inbox draft).
- Gorges are D8 staircases with banded walls at 50 and 25 m (draft).
- River inflow into children is 10-25% short at the 25 m fall (draft).
- Glaciers, landform overlays, deltas and reef forms aren't redrawn at the fine scale (draft).
- Decisions for the owner: 3x3-block means vs per-pixel means; whether to ship the 25 m tier (its canopy is flat) (drafts).
