---
id: PW-1027
title: Globe and zoom draw the same quantity in different colours (10 C is green in the zoom, pale yellow on the globe), and 15+ \"more of something\" ramps rise then fall in lightness
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: []
refs: [viewer/index.html, viewer/zoom.html, viewer/zoom3d.js, planet/thumbs.py, planet/satellite.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-30
---

## Description
In plain words. The zoom is meant to be the same world up close, but temperature, rain and soil fertility change colour on the way in, so you have to learn two keys and can't compare by eye. Separately, many colour scales for "how much" (wave power, tides, floods, sunshine, fire, soil depth, building ground…) get lighter and then darker again, so the lowest and highest values both look dark and the middle reads as the extreme.

Verified on main b36c9581: globe temperature `index.html:452` runs blue → white (0 °C) → yellow → red; zoom `TEMP` (`zoom.html:235`) has green `[120,200,120]` at 10 °C; rain starts tan on the globe and brown `[150,90,40]` in the zoom. The zoom's vegetation/soil ramps are hand-converted copies of the globe's; three volcano palettes (index, zoom, zoom3d). Lightness (CIELAB L*) re-checked with the audit's script: wave power 20→81→58, tide range and upwelling 20→85→58, river floods 39→85→41, turbidity 24→73→33, sunshine 22→87→47, fire return 19→85→45, soil depth 54→79→28, building ground 30→84→64, humidity/dew point/cloud similar.

Fix: one `viewer/ramps.js` (name, unit, kind sequential/diverging/categorical, hex stops) imported by both pages (zoom.html becomes a module); the zoom uses the globe's colours; rebuild the magnitude ramps so lightness only rises or only falls (keep diverging ones, the hypsometric elevation ramp and Köppen colours); a small test checks lightness order for "sequential" ramps; a "stretch to this view" toggle on zoom legends. Show the owner before/after pictures: the ramp choice is taste. (Sharing the Python-side ramps in thumbs/satellite is a separate refactor.)

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-30: Status needs-decision -> todo. Owner 10-30 D2: keep the current ramps (incl. cloud); drop the ramps=new option. Owner dislikes the new pink end colour and skin-tone fertility.
- 2026-10-29: Created from inbox draft draft-colour-ramps-shared-and-monotonic.md (found by code-audit-2026-10).
- 2026-10-30: lane 53: preview behind ?ramps=new (viewer/ramps.js). The zoom draws temperature, rain and fertility with the globe's ramps, and 12 rise-then-fall ramps are rebuilt to run one way in lightness with the same hues (planetViewer.rampReport()). Side-by-sides in docs/review/viewer-ux-sides/. Lean: take the shared zoom ramps, take the one-way rule per ramp, hand-tune fire return. Needs the owner's pick.
