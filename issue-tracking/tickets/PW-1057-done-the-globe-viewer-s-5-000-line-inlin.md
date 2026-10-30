---
id: PW-1057
title: "Done: the globe viewer's 5,000-line inline script is now ES modules (viewer/globe/) with one LAYERS table"
type: task
status: done
parent: null
milestone: null
subsystem: viewer
effort: l
impact: med
found_by: viewer-lane-51
blocked_by: []
relates: [PW-1026, PW-1045, PW-1046, PW-685]
refs: [viewer/index.html, viewer/globe/, viewer/globe/layers.js, viewer/planets.js, tests/test_viewer_globe.py, tools/viewer_perf.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The globe viewer's code used to be one 5,030-line script inside index.html, and each colour layer was defined in about eight different tables. Now index.html holds only the page's markup (5,362 lines down to 330). The code is in 21 small files under viewer/globe/, with no build step. Every layer is one entry in a single table (globe/layers.js). Adding or changing a layer now means editing one place, and a test fails if the entry is incomplete. The viewer looks and behaves the same as before.

What changed (viewer lane 51, audit Q3 and the viewer-code audit's findings 1, 2 and 4):
- **Modules.** main.js's header lists all of them. Shared mutable state now lives in two places:
  - one `S` object in state.js (V, mesh, overlays, the pick, the time-zoom job…)
  - `state` / `proj` for the view's choices
- **LAYERS** (globe/layers.js). Each layer has: label, group, ramp, units, hint, legend, note, the run layers it needs, where its numbers are counted, its categories, seasonal/observed variants, lakes, tint, and which menus show it (`in: {world, run, tz}`).
  - `MENUS` gives the button order.
  - FAMILIES covers 'body: x', 'animal: x' and 'crop: x'.
  - cellColors, availableLayers and layerNeeds read the table.
  - The old RAMPS/UNITS/SEASONAL/… lookups are derived from it.
  - Before replacing the old tables, I checked them against the derived ones with a script: same ramps, units, hints, needs and number-counting areas, and the same menus on 3,000 random fake views. 0 differences.
- **Shared helpers.**
  - Zoom, time-zoom and finish jobs use planets.js `postJob`/`trackJob`. The three hand-rolled poll loops are gone.
  - A local `esc` copy is gone.
  - Four label-sprite builders became one `canvasSprite` (globe/draw.js).
- **Tests.** tests/test_viewer_globe.py checks that:
  - every module parses;
  - the import graph links (node vm, with stand-ins for three);
  - main.js reaches every module;
  - the LAYERS table is consistent.
  - tools/viewer_perf.py now loads the modules.
- **Verification.** About 190 views (a main run, finished world 2a7385, peoples run 3097e3 with Technology), covering every layer button, the slider, hover, click, zoom-into-region, overlays and legends. Screenshots and panel text match the original code apart from the same 4 views that differ between two runs of the original itself (river and name overlays still settling, and run 46730b's frame 0, where the original's globe was still blank when the shot was taken and the modules' was already drawn; the panel text is identical).

One bug fixed: a peoples run made on a time zoom (e.g. 3097e3) offered Plates and Crust age, but it carries no plate or crust layers, so clicking either threw "Cannot read properties of undefined (reading '0')" and left the old colours up. A time zoom now shows those two buttons only when its run has the layers.

Small differences, all on error paths:
- A zoom the server refuses with its own 404 message now shows that message.
- An unreachable server says "not reachable" instead of "no API, restart it".

Follow-ups are in their own drafts (draft-viewer-time-formatters, draft-globe-draw-helpers, draft-viewer-module-order-check).

## Updates
- 2026-10-30: Created from inbox draft draft-globe-viewer-modules-done.md (found by viewer-lane-51).
