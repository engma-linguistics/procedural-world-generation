---
id: PW-505
title: "Viewer: show the human-use layers (navigable rivers, harbours, passes, farmland, fresh water)"
type: task
status: done
parent: PW-099
milestone: v1
subsystem: viewer
effort: s
impact: med
found_by: humanuse
blocked_by: []
relates: [PW-099]
refs: [planet/humanuse.py, viewer/index.html, viewer/zoom.html]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-099 stores five class-map layers with every finished world and zoom (`river_nav`, `harbour`, `pass`, `fertile`, `fresh_water`, plus `pass_height`, `fertile_score`, `fresh_km`, `spring`) and puts their legends in `S.legends()["human_use"]` (also in each file's `legend`). The viewer was not touched (another agent was changing `viewer/`, `server.py` and `api.py`). The layer pickers are hard-coded lists (`SOIL_LAYERS` in `viewer/index.html`, the layer table near `soil_fertility` in `viewer/zoom.html`), so adding them is a list entry plus a legend-coloured class map per layer, and a hover-card line (pass height and open months, harbour class, farmland class).
- [ ] world viewer: five class-map entries coloured from the legend, hover-card lines
- [ ] zoom viewer: the same; springs and passes as markers
- [ ] older worlds have no stored layers: the viewer shows nothing for them (or the API computes them with `humanuse.analyse_world`)

## Updates
- 2026-10-21: Status todo -> done. Done: five layers as buttons on the globe (colour maps; ribbons for navigable rivers, markers for harbours and passes under Overlays), 2D map (projmap.drawFeatures), zoom tab (class maps, harbour/pass/spring markers, hover rows); planet humanuse backfills old worlds and zooms. Verified on 577526 + zooms 66c45e, 21703a (backfilled copy). Follow-up draft: humanuse-3d-markers-backfill.
- 2026-10-21: Created from inbox draft draft-humanuse-viewer-layers.md (found by humanuse).
