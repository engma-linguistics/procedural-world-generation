---
id: PW-1042
title: "The time slider has no dates and uneven steps (15 moments for 19 Myr take as much room as 21 in the last 10 kyr): give it the workbench's log axis"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: m
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-918]
refs: [viewer/index.html, viewer/lineages.html, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The slider at the bottom of the globe moves one stored moment per step, with no dates on it. On a peoples run, 19 million years take the same room as the last 10,000 years, so where the handle sits tells you nothing about when you are. "Go to 12,000 years ago" is guesswork. The keyboard shortcuts are only in tooltips.

From the viewer-ux audit: `index.html:312-317` (`#timeline`, `#frame` 0..frames-1), `timeLabel()` ~3133; run 3097e3 has 153 moments (15 before 1 Myr ago, 117 between 1 Myr and 10 kyr, 21 in the last 10 kyr).

Fix (mock-up §3): reuse the workbench timeline's log axis with era bands (`lineages.html:244-296`) on peoples runs and time zooms; ticks at 10 Myr, 1 Myr, 100 kyr, 10 kyr, 1 kyr; event marks on the same axis; a short key hint. Main runs keep a linear axis, with ticks.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-time-slider-axis.md (found by code-audit-2026-10).
