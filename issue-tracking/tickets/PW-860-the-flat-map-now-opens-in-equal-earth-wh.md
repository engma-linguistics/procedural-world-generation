---
id: PW-860
title: The flat map now opens in Equal Earth, which draws no overlays (highlights, events, rivers, markers); port them or default smartly
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: m
impact: med
found_by: fun-lane-24
blocked_by: []
relates: [PW-838]
refs: [viewer/index.html, viewer/projmap.js]
created: 2026-10-25
updated: 2026-10-25
---

## Description
PW-838 (owner) made the flat map default to Equal Earth. The projected maps (`projmap.js` canvas) draw only the layer colours, no overlays: highlight rings and number labels, event markers, rivers, peoples' origin rings, volcanoes. So the default flat map shows none of them until the owner switches the projection to Equirectangular or ticks 3D relief (which keeps the live three.js map). Options: (A) leave it and say so in the tooltip (as now); (B) project the overlay points through `makeProjection` and draw them on the canvas (highlights and events first); (C) keep Equal Earth as the default only when no overlay is ticked. Lean B for highlights and event markers, since the owner looks at highlights on the flat map.

## Updates
- 2026-10-25: Created from inbox draft draft-flat-map-projections-lack-overlays.md (found by fun-lane-24).
