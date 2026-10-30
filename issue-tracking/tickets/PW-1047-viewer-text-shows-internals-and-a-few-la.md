---
id: PW-1047
title: "Viewer text shows internals and a few layouts break: \'Time zoom and events\' on peoples runs, a stale floating tooltip, unlabelled log bars, cut-off tech names, CLI lines in owner-facing help"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-841]
refs: [viewer/index.html, viewer/lineages.html, viewer/techtab.js, viewer/zoom.html, docs/review/code-audit-2026-10/img/, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. A batch of small things that make the viewer feel unfinished: the peoples run's summary is titled "TIME ZOOM AND EVENTS"; the floating hover tip follows the mouse onto the side panel and keeps showing old text; a cell's details appear in two places at once; the workbench shows "1.3e+02 Mkm²" and a log-scale population bar without saying so (310 M and 1.6 M look almost equal); tech names are cut mid-word ("bread and flatbread bakin"); the landmass table's rows stretch with a 340 px gap and long names run off the edge; the workbench header mixes tree-file and run actions over two ragged rows; and several help paragraphs tell you to type `uv run python -m planet ...`, though you use the viewer, not the command line.

From the viewer-ux audit (screenshots g2-5/6/7, l-results, l-tech, l-0): `index.html:3122` (`V.tz ? 'Time zoom and events'`), `lineages.html:762` (`Math.log10` bars), `lineages.html:61-76` header.

Fix:
- [ ] plain titles ("Peoples and events"); one number formatter everywhere
- [ ] hide the tooltip on pointerleave; on the globe use the card, not both
- [ ] linear bars or a labelled log scale
- [ ] ellipsis + full name on hover for tech boxes; landmass table rows size themselves, short names
- [ ] workbench header in two groups (Tree: picker, Save, Save as, Import/Export; Run: world, tries, Run, status); help text in "?" popovers without CLI lines

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-viewer-text-and-layout-polish.md (found by code-audit-2026-10).
