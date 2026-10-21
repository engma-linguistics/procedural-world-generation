---
id: PW-092
title: Zoom synthesis from the glacial imprint
type: story
status: done
parent: PW-090
milestone: v1
subsystem: zoom
effort: l
impact: high
found_by: daniel
blocked_by: [PW-037]
relates: [PW-005, PW-010]
refs: [planet/zoom.py, "plan_next@bdc967f: Known issues → Rivers, lakes, sediment", "plan_next@bdc967f: Known issues → Highlights"]
created: 2026-10-14
updated: 2026-10-21
---

## Description
From the glacial imprint layers (PW-037), the zoom synthesises: U-shaped valleys, cirques and arêtes,
fjords; hanging valleys with waterfalls (ties to the escarpment / landform work, PW-005); moraines,
drumlins and eskers; kettle and finger lakes.

Merged known issues: "No glacial hanging valleys" (`falls`) and "Fjords aren't carved in the zoom; fjord
coasts are only detected" (`zoomwater`).

## Updates
- 2026-10-21: Status todo -> done. Closed for v1 (2026-10-21): done at the regional zoom's scale; ice flow direction and the rest in PW-499 (v2).
- 2026-10-21: Done at the regional zoom's scale (pw092; docs/review/audit/PW-092-handoff.md, overview 11b): troughs with overdeepened basins and hanging valleys, cirques, fjords, moraine ridges, drumlins, kettles, outwash and loess from the imprint, in `planet/zoom_glacial.py` as a Synth of zoom_landforms. Showcase: world 577526 (Earth, 420 kyr of e9d59c; f6e955 re-finished, it had no rock): Norway 66c45e (14 fjords to 835 m), Ungava 4f65aa, Baltic margin 21703a, Alps b03a2b, Patagonia bf3c88 (the last two ~nothing: their imprint is ~0), Norway 1 km 0de6eb. Open: moraine-dammed lakes, fine zooms, Alps/Patagonia imprint, calibration (drafts filed).
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14). Merged 'No glacial hanging valleys' (falls) and 'Fjords aren't carved in the zoom' (zoomwater), which were first placed in PW-012.
