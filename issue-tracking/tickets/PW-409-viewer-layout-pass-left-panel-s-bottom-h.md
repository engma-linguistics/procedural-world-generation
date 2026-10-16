---
id: PW-409
title: "Viewer layout pass: left panel's bottom hidden under the legend bar; zoom 3D right pane overlaps its sections"
type: task
status: todo
parent: null
subsystem: viewer
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-072]
refs: [viewer/index.html, viewer/zoom.html]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner screenshots 2026-10-16:
- Globe/map page: with sections expanded (Highlights, Overlays, Display, Sliders), the left panel scrolls under the bottom legend bar (elevation scale and the symbol legend), so the last controls (river threshold etc.) can't be reached. The panel must end above the legend, or the legend must sit outside the panel's column; check at 1080p and smaller windows.
- Remove the "Why pentagons?" section from that panel (owner: not needed).
- Zoom 3D view: the right pane stacks the 3D controls, the fly-along-a-river and waterfalls sections, and the hover cell card on top of each other. The cell card (x,y, elevation, rock, climate, plants, soil...) overlaps the waterfalls list and is cut off. Make it one scrolling column, or dock the cell card separately, so every section is readable; collapsible sections are fine.
Do both in one pass; screenshot before/after.

## Updates
- 2026-10-16: Created from inbox draft draft-viewer-layout-pass.md (found by daniel).
