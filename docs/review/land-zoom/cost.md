# Land zoom cost: where a 4000 km section's time and memory go (PW-1303, epic PW-1299)

Lane 122, 2026-11-02. Section `world:dba204(-25.0, 65.0)`, 4000 km. Harness (scratchpad, not committed): wraps each `stage_*`
function of `regional.build`, samples process RSS every 50 ms for the per-stage peak, and hashes every output array.

## In plain words

Lane 116's 2 h 48 m for a 1 km section was almost all one bug-like loop, not the terrain: the human-use layer (`humanuse.py`
mountain-pass finder) ran a whole-raster shortest-distance search once per pass found (188 times, each over 16 M pixels at
1 km). Making each search look only at the window round its pass cut that stage from ~12 min to ~10 s at 2 km and the 1 km
section from **2 h 48 m to 16 m 16 s** (the whole `planet zoom`, including saving). The memory peak was one block in the
landform pass that compared every pixel with every landform cell at once (22 GB at 2 km); doing it in pixel blocks cut that
stage's peak from 29.3 to 8.8 GB and the section's peak at 2 km from 29.4 to 23.1 GB, at 1 km from 110.4 to **85.9 GB**.
Outputs are the same: all 81 output arrays hash identically before and after (landform change; the pass change was checked on
the stored zoom 7b69a9: pass and pass-height layers identical). Two sections now fit side by side (86 GB each; 183 GB total),
not several: the rest of the memory is spread thin (see below).

## Per stage at 2 km (4000 km, one lone run; wall s / peak RSS GB)

Before (original code) -> after. Only stages that changed are called out; the others are the same within noise (a second
"before" run took 1008 s because I ran another job beside it).

| stage | before | after | what it does |
|---|---|---|---|
| frame_and_grid, coarse_fields, delta_plains, coastline, detail | 0.8, 6.7, 2.2, 5.0, 0.5 s; peak <= 3.3 GB | 0.3, 4.0, 1.8, 4.4, 0.3 s | pixel grid, coarse fields interpolated on it |
| mean_correction | 39.2 s, 3.3 GB | 41.7 s, 3.2 GB | per-cell mean undo (largest remaining serial-looking stage; not profiled further) |
| volcanoes, tides_and_flats | 7.3, 1.6 s | 7.8, 1.7 s | |
| landform_classes | 29.2 s, **29.3 GB** | 27.6 s, **8.8 GB** | `landforms.py::zone_stats` nearest-landform-cell search, now in pixel blocks |
| coarse_rivers .. fit_setup | ~9 s, 7-8 GB | ~9 s, 7-8 GB | |
| landscape_loop | 36.7 s, 10.2 GB | 35.6 s, 10.1 GB | 15 stream-power iterations (flood fill, routing, falls); numba kernels |
| final_drainage, shoreface, crop_halo | 7.2, 3.1, 0.2 s | 6.1, 3.2, 0.2 s | |
| climate_on_terrain | 4.5 s, 12.0 GB | 4.6 s, 11.8 GB | |
| vegetation_layers | 24.7 s, **23.4 GB** | 18.4 s, **23.1 GB** | `zoom/vegetation.py::compute`; now the peak (transient ~8 GB over its 15 GB floor) |
| coastal_life, ice_bed | 5.4, 0.0 s | 5.3, 0.0 s | |
| stats | **603.4 s** (one core), 20.2 GB | **20.4 s**, 19.6 GB | of which `humanuse.zoom_layers` 741 s -> ~10 s (`passes()`), gameattrs 6-8 s, satellite 5-6 s |
| build total | 788 s (lone) | 194 s | |
| after build (`save`, coast layers, deposits) | not timed | 1 km: ~65 s in all | |

At 1 km (`planet zoom dba204 --lat -25 --lon 65 --size-km 4000 --res-km 1`, 16 M px): build 911.6 s, wall 16 m 16 s,
713% CPU, peak RSS 85.9 GB (before: 2 h 47 m 42 s, 110.4 GB). Free memory was 162 GB available and /tmp 87 GB free at the start.

## What was changed

1. `planet/humanuse.py::passes` (+ `Net.shape`, new `dist_near`): the "keep only the lowest pass within ~40 km" step called
   `dist_from` over the whole raster per kept pass (the `np.minimum.at` edge relaxations, 188 x ~4 s at 2 km, ~8x worse at 1 km). On a zoom it
   now runs the same relaxation on the window that a path of that length can reach (same edges, same weights, same iteration
   count), so the distances are identical. World nets are unchanged.
2. `planet/zoom/landforms.py::zone_stats`: the pixel-to-nearest-class-cell search made an (npx x 256) float block plus two
   temporaries; it now works in pixel blocks of about 4 M distance values. Same arithmetic, same first-minimum tie rule, same result.
3. `planet/zoom/regional.py::Frame(lat, lon, up=None)`: new optional orientation for the tiling (PW-1319); default unchanged.

Nothing else was tried: no strikes used.

## What is left (drafts filed)

- Memory floor and the vegetation peak: RSS at the end of the terrain stages is 15 GB while the arrays the build holds (deep
  count of `ctx`) are ~6 GB (landforms `lf` 2.7 GB, fields 0.8, vegetation/terrain 0.9): tracemalloc says 10.6 GB live at
  the end of `vegetation_layers` and the rest is allocator/runtime overhead. The vegetation pass transiently adds ~8 GB
  (many 0.4-1.8 GB arrays in `zoom/vegetation.py::compute`: 12-month and per-plant-type fields over all pixels). Chunking it by
  pixel rows (it is per-pixel) is the next memory step; the target for "several at once" is ~35-40 GB at 1 km.
- Serial stages that remain: `mean_correction` (42 s at 2 km) and the 15-iteration `landscape_loop` (36 s): at 1 km ~5 min each; fine for now.
- GPU: not needed for this cost; the 2 h stage was a CPU algorithm problem, not a heavy kernel.
- A 47-section planet at 1 km (dba204; `tiling.md`) is about 47 x 16 min = 12.5 h of one-at-a-time compute, or ~6.5 h with two at once.
- Storage of a section: not measured here.
- Note: the 1 km run reuses the id of lane 116's 1 km cost zoom (69b422; ids come from the world, centre, size, res and seed),
  so it overwrote that zoom, and I deleted it after (it was the cost-only run).
