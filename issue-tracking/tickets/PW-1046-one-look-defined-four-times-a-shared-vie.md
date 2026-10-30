---
id: PW-1046
title: "One look defined four times: a shared viewer/theme.css for colours, buttons and inputs (sliders and checkboxes are browser-default blue today)"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-410]
refs: [viewer/index.html, viewer/zoom.html, viewer/lineages.html, viewer/ringworld.html, viewer/start.js, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The four viewer pages look alike but each defines its own colours and button styles, slightly differently, so sliders and checkboxes show the browser's bright default blue in places, the workbench has a raw "Choose File / No file chosen" box, and section headings' triangles sit above the text. One shared style file would fix these at once and make every later redo cheaper.

From the viewer-ux audit: `:root` tokens copied in index.html:8-11, zoom.html:8-11, ringworld.html:8; lineages.html:8 has its own (`--acc`, system-ui font); three button background shades (#111827, #1c2536, #1d2532); 165 hex literals in index.html, 36 in zoom.html, 42 in techtab.js.

Fix: `viewer/theme.css` with the tokens, base button/select/input styles, `accent-color: var(--accent)`, one section-heading style and a styled file button; each page links it and keeps only its own layout.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-viewer-shared-theme.md (found by code-audit-2026-10).
