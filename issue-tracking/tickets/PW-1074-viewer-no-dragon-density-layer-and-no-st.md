---
id: PW-1074
title: "Viewer: no dragon-density layer, and no stored peoples run with the food-budget dragons (lanes 43-45b) to show one"
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: m
impact: med
found_by: dragon-density-doc
blocked_by: []
relates: [PW-977, PW-990]
refs: [viewer/index.html, docs/review/megafauna/dragon-density/shot.py, docs/review/megafauna/dragon-density/charts.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** The owner reads results in the viewer, but the viewer cannot show how many dragons live where. The dragon-density report had to draw its own map instead.

- The newest peoples run on 2a7385 is 3097e3 (2026-10-27), from before fun lanes 43-45b, so its dragon counts follow the old density
  rule. The 45b densities exist only in the lane's tmpfs probe saves (ERAS.npz, RUN.npz).
- The viewer's peoples layer shows a dragon kind's range when it is picked in the panel, but not its density. In a headless Chrome
  (swiftshader) the pick set the panel's "show all" link but did not redraw the globe, so the report could not screenshot a picked
  dragon kind (docs/review/megafauna/dragon-density/shot.py).

Wanted: a "dragons" layer reading a per-cell expected-dragons field the run stores (every kind, per 1,000 km², log colour), next to
the peoples layer, as in the report's Figure 6 (charts/map.png). It also serves the abundance slider of PW-990 stage 3.
- [ ] the run stores expected dragons per cell at each frame (or the present)
- [ ] a viewer layer for it, matching the peoples layer's style
- [ ] a fresh dnd run on 2a7385 with the current model, for the showcase

## Updates
- 2026-10-30: Created from inbox draft draft-viewer-dragon-density-layer.md (found by dragon-density-doc).
