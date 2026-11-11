---
id: PW-1694
title: "LOD tiles: carve the ground at tile edges in a place-keyed block, so the edge strip is neither smoother nor rougher than inside"
type: task
status: done
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: l
impact: high
found_by: lane290
blocked_by: []
relates: [PW-1689, PW-1688]
refs: [planet/zoom/fine.py, "planet/zoom/fine.py::build", "planet/zoom/fine.py::EDGE_TEXTURE", planet/zoom/lod_build.py, tests/test_zoom_lod_build.py, docs/review/zoom/lod-plan-v2.md, "world dba204", "cell py.1.1"]
created: 2026-11-10
updated: 2026-11-11
---

## Description
**In plain words.** Detail tiles built at different times now meet without a cliff, but near each tile edge the ground is
not quite like the ground inside: within ~8 pixels of the edge, the eroded valleys and ridges that the landscape pass carves
fade out into the parent's ground plus a texture made from noise. On world dba204 the height steps across four shared edges
are 0.78-1.09x the steps inside (median) and 0.68-1.54x (the 90th percentile); on the test's synthetic hills 0.53x. So on
the Google-Earth globe some tile edges will show as faint smoother (or bumpier) lines a few pixels wide. If this is never
done, the tile grid stays faintly visible in mountains, which is what the seam work was meant to remove.

Why: the carving depends on the whole area a tile builds, so two tiles can only agree at their shared edge on a surface that
depends on the place alone. Today that surface is the parent's ground + the detail noise + `fine.EDGE_TEXTURE` x relief
noise (lane 290, set from dba204); one constant cannot match carved ground in every terrain (measured above).

The fix (plan 2.2 item 3, done properly): run the landscape pass a second time on a block that depends only on the edge
(e.g. a strip 2 x 16 px wide centred on the shared edge, its ends overlapping a corner block centred on each tile corner),
from the same parent window; both siblings compute the same block, so the edge pixels are carved ground on both sides; fade
from the tile's own pass to the block's over the strip (variance-kept mix, as now). Cost: ~4 thin strips and 4 corner blocks
per tile, ~+35% pixels for the landscape pass only (the rest of the build is unchanged); needs the pass split out of
`fine.build` (a ~300-line section) so it can run on a block.
- [ ] tests/test_zoom_lod_build.py::test_edge_steps_like_the_inside passes (remove its xfail) and the four dba204 seams of
      cell py.1.1 level 2 (tiles 4/4, 5/4, 4/5, 5/5) have land-step ratios (median and p90) within 0.9-1.1
- [ ] rebuilds stay bit-identical; per-tile time and peak re-measured

## Updates
- 2026-11-11: Status todo -> done. Merged lane 293 (04c27b81): edges carved on place-keyed blocks; edge ratio within 0.01-0.05 of the seamless line. Criterion question: PW-1697.
- 2026-11-10: Created from inbox draft draft-lod-edge-carving.md (found by lane290).
