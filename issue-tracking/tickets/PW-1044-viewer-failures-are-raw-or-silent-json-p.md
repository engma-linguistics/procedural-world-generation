---
id: PW-1044
title: "Viewer failures are raw or silent: JSON parse errors in a corner box, no loading sign, a dead-end \'zoom\' offer on peoples runs, and fetches that ignore failures"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-914]
refs: [viewer/index.html, viewer/zoom.html, viewer/lineages.html, docs/review/code-audit-2026-10/img/, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. When something goes wrong you get a programmer error ("Unexpected token '<' … is not valid JSON") in the small hover box, half-built panels and an enabled Delete button with nothing loaded. When a layer is loading, nothing says so: the button lights up but the old picture stays for seconds. Clicking a cell on a peoples run offers "Zoom into this region" and then tells you it can't, with no button to go where it can. Behind the scenes, a few loads can quietly go wrong: picking two runs quickly lets the slower one win, a missing zoom layer file is decoded as if it were data, and a server restart during a peoples run stops the progress display without a word.

From the viewer-ux and viewer-code audits (spot-checked: `lineages.html:898-909` polls with no catch around the loop; `zoom.html:458` fetches layers without checking `r.ok`): `index.html:4371` dead-end message; `loadRun` (~4884) and `setWorld` (~4780) assign `V` after several awaits with no "latest wins" guard.

Fix:
- [ ] a centred error card naming the item in plain words, with recent planets and a link to the start page (mock-up §4); Delete disabled with nothing loaded
- [ ] a small spinner / dimmed button until the new layer is painted
- [ ] "Open the source run here" button in the dead-end box
- [ ] load token (`if (tok !== loadSeq) return`) after each await in loadRun/setWorld/zoom load
- [ ] `fetchLayer` throws on !ok; the lineages poll uses planets.js `trackJob` (which survives restarts) and posts with Content-Type

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-viewer-error-and-loading-states.md (found by code-audit-2026-10).
