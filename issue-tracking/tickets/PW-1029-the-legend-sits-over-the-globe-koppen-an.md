---
id: PW-1029
title: The legend sits over the globe (Koppen and peoples legends hide a third of it) and has the event filters mixed in without a heading
type: task
status: needs-decision
parent: null
milestone: null
subsystem: viewer
effort: s
impact: high
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-409]
refs: [viewer/index.html, viewer/techtab.js, docs/review/code-audit-2026-10/img/, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-30
---

## Description
In plain words. The colour key is drawn on top of the map at the bottom left and grows with the layer: the climate key (30 entries) and the peoples key (45 entries) cover the lower third of the globe. Ten unlabelled checkboxes for event rings (root, split, crossing…) are tucked into it, and the rings' colours are never explained. The Technology map shows two keys that word the same things differently.

From the viewer-ux audit, seen in screenshot g2-2: `#legend` placed over the canvas, filled ~index.html:2790; event-kind checkboxes appended inside it.

Fix (mock-up §2): dock the legend in the right column above the summary; start with name, season and unit, then a bar with 5-6 ticks, the hovered value marked; cut long category lists to the top 8 by area with "+N more"; move event filters under Overlays, each with a ring of its colour; one legend per Technology view.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-legend-docked-out-of-the-map.md (found by code-audit-2026-10).
- 2026-10-30: lane 53: preview behind ?legend=dock, which moves the legend into the right-hand column above the summary. Side-by-sides at 1600x1000 and 1280x800 in docs/review/viewer-ux-sides/. Lean: dock it. The event filters stay in the legend for now. Needs the owner's pick.
