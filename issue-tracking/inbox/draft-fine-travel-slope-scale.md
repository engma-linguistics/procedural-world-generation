---
title: Fine-zoom travel and fertile read slope at the pixel, so a rung's travel time is 1.6-3.3 x-units above its parent's
type: task
status: needs-decision
parent: PW-1198
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: lane285
blocked_by: []
relates: [PW-1679, PW-206]
refs: [planet/gameattrs.py::zoom_layers, planet/humanuse.py::analyse_zoom, planet/zoom/fine_layers.py, docs/review/zoom/fine-layers.md, "zoom 44d6d6", "zoom 01f501"]
---

## Description
**In plain words.** The walking-time layer (`travel`) and the farmland slope penalty take the ground's slope from the pixel
neighbours. At 25 m a mountain slope is steeper than the same ground at 0.5 km or 2 km, so a 30 km rung reads slower than the
rung above it: see docs/review/zoom/fine-layers.md, mountain chain 2a4463 > 44d6d6 > 01f501, travel mean difference to the parent
+0.34 at the 44d6d6 edge, +1.85 in its interior, +1.58 at the 01f501 edge and +3.28 inside (scale 0 to 12.5). Lane 285 kept the
pixel-scale slope because walking and ploughing respond to slope over tens of metres, so the finer reading is arguably the right one;
the edge step is what a viewer will see when two rungs sit side by side.

Options: A keep (finer ground is rougher: document it); B read slope over a fixed ~100 m scale at every pixel size (a km window,
as `vegetation.cell_relief` does for relief), which removes the step but loses 25 m cliffs; C blend the two over the outer parent
pixel at a rung's edge. Lean A, with B if the viewer's seam is judged ugly. What breaks if never done: nothing crashes; two
overlays differ by a visible step at a rung's edge in rugged country.
