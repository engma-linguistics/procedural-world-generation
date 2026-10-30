---
id: PW-1046
title: "One look defined four times: a shared viewer/theme.css for colours, buttons and inputs (sliders and checkboxes are browser-default blue today)"
type: task
status: done
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
updated: 2026-10-30
---

## Description
In plain words. The four viewer pages look alike but each defines its own colours and button styles, slightly differently, so sliders and checkboxes show the browser's bright default blue in places, the workbench has a raw "Choose File / No file chosen" box, and section headings' triangles sit above the text. One shared style file would fix these at once and make every later redo cheaper.

From the viewer-ux audit: `:root` tokens copied in index.html:8-11, zoom.html:8-11, ringworld.html:8; lineages.html:8 has its own (`--acc`, system-ui font); three button background shades (#111827, #1c2536, #1d2532); 165 hex literals in index.html, 36 in zoom.html, 42 in techtab.js.

Fix: `viewer/theme.css` with the tokens, base button/select/input styles, `accent-color: var(--accent)`, one section-heading style and a styled file button; each page links it and keeps only its own layout.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-viewer-shared-theme.md (found by code-audit-2026-10).
- 2026-10-29: Viewer lane 51 split the code into modules. index.html is now markup and CSS only (330 lines, its `<style>` unchanged), so a shared theme.css only has to touch the `<style>` blocks of the four pages. Colours used in JS are in globe/layers.js (ramps, legend swatches) and globe/colours.js.
- 2026-10-30: Viewer lane 53: viewer/theme.css holds the tokens (bg, panel, panel-solid, text, muted, accent, on-accent, border, ctl, ctl-hi, ctl-sel, err, ok, star, font, mono), accent-color for checkboxes, radios and sliders, the base select/input/code/.btn/.seg styles, a styled file button, the section-heading style and the collapsible-section triangle (no longer raised above the text). index.html, zoom.html, ringworld.html and lineages.html link it and keep only their layout; the start screen, navigator, pick filter, planets.js and the Technology tab's injected CSS use the tokens instead of #111827 / #06121f / #ffc940 / #1d2532 / #1c2536. Pixel diff against before: the globe page changes only in the section triangles (0.1% of pixels); ringworld in its button shade and accent sliders; the workbench takes the shared background, text colour and font (it was system-ui), and its 'Choose File / No file chosen' box is an 'Open JSON…' button.
