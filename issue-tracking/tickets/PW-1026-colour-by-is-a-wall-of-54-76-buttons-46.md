---
id: PW-1026
title: "\'Colour by\' is a wall of 54-76 buttons (46 on the zoom): group it, add search and recent, one picker each for crops/animals/body traits"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: m
impact: high
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-410]
refs: [viewer/index.html, viewer/zoom.html, docs/review/code-audit-2026-10/img/mock-redo.jpg, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The most-used control is a flat block of 54 buttons on a peoples run, 76 on a finished world and 46 on the zoom. 30 of them are "crop: …" and "animal: …", some with code names (crop: foxtail_millet). The panel is so tall that Overlays and Display sit below the fold. Finding a layer means reading 50 labels every time.

From the viewer-ux audit (counts from its screenshots; layout seen in g1-1/g2-2): `index.html #layerSeg` (seg('layerSeg', …) ~line 4100), `zoom.html #layerSeg`.

Fix (mock-up §1 in the audit page): a search box; a "recent" row of the last 4 layers; collapsible groups (Land and sea, Climate, Plants and soils, Peoples, Food and kit, Game and use, Coast and sea); one dropdown each for crop, animal and body trait like the existing tech/resource/plant-type pickers; display names with spaces. Same groups and names on the zoom page. `?layer=` links keep working because keys don't change.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-colour-by-grouped-picker.md (found by code-audit-2026-10).
- 2026-10-29: Viewer lane 51 split index.html's script into viewer/globe/ modules. Every layer is now one entry in `LAYERS` (globe/layers.js), with a `group` (surface, geology, ice, glacial, climate, air, water, plants, soil, game, humanuse, resources, coasts, sea, peoples). `MENUS` gives the button order, and the 'body:', 'animal:' and 'crop:' families are expanded in one place (FAMILIES). The grouped picker can read groups, labels and hints straight from the table; panel.js `renderLayerButtons` is the only place to change. zoom.html still has its own list.
