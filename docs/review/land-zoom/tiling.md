# A tiling of the sphere by land-zoom sections (PW-1319, epic PW-1299)

Lane 122, 2026-11-02. Code: `planet/zoom/tiling.py::sections`, test `tests/test_zoom_tiling.py`. Nothing is zoomed by this lane.

## In plain words

Lane 116 found that stepping "3800 km east" from a section does not give a neighbouring square (the squares rotate and
drift, one overlap was 871 km instead of 200). The fix is to decide the sections **first**, from a fixed cut of the whole
sphere, and zoom each one on its own cell. I use a cube cut into a 3 x 3 grid per face (54 cells). Each cell has one
4000 km section centred on it and turned so its "up" is the face's own up, so neighbours' squares are parallel to the
edges they share. Every cell lies inside its section with at least 97 km to spare on every side, so two neighbours overlap
by at least 197 km (typically 197-256 km; much more where a big cell meets a small one). On dba204, 47 of the 54 sections
hold land worth zooming (a section whose home cell holds under 5% of an even share of land is skipped; those 7 hold 242 of
58,578 land cells, 0.4%).

## The rule

1. **Cells.** Cube faces `px py mx my pz mz` (normals +-x, +-y, +-z), each cut 3 x 3 by great circles. A point of a face is
   described by two angles (a, b) with tan(a) and tan(b) along the face's u and v axes, each within +-45 degrees. The edges
   between cells sit at a = +-17.1 degrees (the plain equiangular cut would be +-15; it makes the corner cells of a face too
   big for a 4000 km square, margin -26 km, so the edges are pushed outwards: edge = 45 degrees * (1/3)^0.88, `WARP = 0.88`,
   the value that maximises the least margin, found by scan: 0.88 gives 97 km, 0.90 77, 0.86 55, 1.0 -26). Cell ids are
   `face.i.j`, e.g. `px.1.1` (centre 0 N 0 E).
2. **The section of a cell** is a `Frame` (azimuthal equidistant square, 4000 km) centred on the cell's centre, with its
   +y axis along the face's v axis (north-up is not used: `Frame(lat, lon, up=...)`, new in this lane, default unchanged).
   All six faces use their own up, so the section's orientation is shared by all cells of a face and changes by a quarter turn
   or so across a cube edge; the overlap with a neighbour on another face is still a band, because both squares contain the
   shared great-circle edge with margin.
3. **Which section owns a place:** the cell that contains it (`locate`). The section's output is trusted inside its own cell;
   the margin beyond the cell edge is the overlap band for blending or for checking seams (the seam line of
   `seams.py` is the shared cell edge, the great circle between two cell centres' bisector is not needed).
4. **Margin and overlap** (`margin_km`, computed from 24 points per cell edge in the section's own plane, so it includes the
   projection's distortion): the least distance from the cell's boundary to the section's edge is 97 km (quartiles over all
   54: 97, 99, 99, 159, 159). The overlap between two neighbours is the sum of their margins at the narrowest place: 197
   to 256 km at worst for every pair; the widest pair slack is 1884 km (a small corner-side cell next to a big middle cell).
   Cell widths along a face's middle line: 3806 km (centre cell), 3101 km, 2870 km (corner cell). A cell of 3806 km inside
   4000 km is why 97 km is all that fits; a bigger overlap needs a larger square (4096 px caps a section at about 4.1 x res) or n = 4 (96 sections, margin >= 428 km).
5. **Neighbours** (`neighbours`): ids of the cells that share an edge or a corner (3-8 per cell; a face-corner cell has 3
   neighbours at a cube corner plus the others across the edges; the face-middle cell has 8). `overlap_km` is the least overlap with any of them.

## How many sections cover dba204's land

`sections(world)` keeps a cell when it holds land cells (the world's land mask `world_land`) at least `min_land_frac` (0.05)
of an even share (163,842 cells / 54 = 3,034 per cell).

| keep cells with | sections |
|---|---|
| any land cell | 53 |
| >= 1% of an even share | 51 |
| >= 5% (default) | **47** (99.6% of the land cells) |
| >= 10% | 39 |
| >= 25% | 32 |

This is more than the 15-20 lane 116 guessed from land area (36% land x 510 M km2 / 16 M km2 = 11.5 squares at perfect
packing): the land is scattered over the cube's cells and a fixed cut cannot slide to the continents. Ways to bring it down
(draft filed): drop a thin-land cell whose land already lies inside a neighbour's square with margin (a set cover on the
land rather than the cell), or shift the cube (rotate it as a whole) to the orientation that has the fewest land cells
on cell edges; both only need this function's `margin_km` machinery on land points.

Cost at 4000 px (1 km/px) is in `cost.md`: 47 sections x that time.

## What is not done

- `zoom()` does not take an `up` yet: `Frame(..., up=...)` exists and `sections()` returns `lat`, `lon`, `up`, but
  `regional.build/zoom/save` and `zoom.json` (`center` only) do not carry the orientation, nor does `seams.py` (it rebuilds the
  frame from `center`). That is the first step of the sweep ticket.
- No section was zoomed and no seam re-measured (the ticket's second checkbox needs the sweep).
- The polar faces (`pz`, `mz`) have their centre cell at the pole; `Frame(up=...)` handles it; `Frame(lat, lon)` alone does not give a defined east there.
