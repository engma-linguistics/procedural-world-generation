---
title: "LOD tiles: a waterfall whose gorge crosses a tile edge is still drawn by neither tile"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane293
blocked_by: []
relates: [PW-1695, PW-1694, PW-1689]
refs: ["planet/zoom/fine.py::build", "planet/zoom/fine.py::_fall_chain", "planet/zoom/fine.py::_gorge_path", planet/zoom/lod_build.py, tests/test_zoom_lod_build.py, docs/review/zoom/lod-plan-v2.md]
---

## Description
**In plain words.** On the zoomable globe, a waterfall whose lip-to-foot gorge runs within ~8-10 pixels of a tile's edge
is left out of both tiles: the river just runs on without its drop or gorge, and the fall is missing at every finer level
too (finer tiles read falls from their parent's stats). If never done, some falls on the globe vanish depending on where
the tile grid happens to fall.

Lane 293 (PW-1695) made volcanoes keyed by place (every tile whose built area the cone reaches draws it from the same
parent data, the summit found on the whole hold on the lattice, listed in each tile's stats with `owner`) and made a
fall's own numbers keyed by place (the relief scale from the planet, the gorge's rock along its whole path, the tier
draw seeded by the lip's lat/lon). But `fine.build` still skips a fall when its chain comes within `ramp` of the built
area's edge (seam=True or not): drawing it partially needs the gorge code (lip/foot/path pixel sequence `seq`, the
cut region `ib`, the plunge pools, `hw[seq]`, `c_rec`) to accept a lip or foot outside the tile, which it doesn't.

What to try: in seam mode, run the gorge on the fall's own lattice window (lip-to-foot path plus its wall margin, keyed by
place, like the volcano's hold disc in `build`), then copy the cut onto the tile's pixels that fall inside it; pass the
fall to the tile's stats with `owner` (the tile holding the lip). The edge blocks (lod_build.edge_blocks) then draw it too.
- [ ] a fall placed on a shared edge of two synthetic sibling tiles: drawn on both sides (its drop on the lip's side, the
      gorge on both), no step across the edge beyond the inside steps, listed in both tiles' stats
