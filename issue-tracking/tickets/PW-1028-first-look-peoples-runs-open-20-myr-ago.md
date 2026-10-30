---
id: PW-1028
title: "First look: peoples runs open 20 Myr ago (nobody exists yet), the zoom opens under 1,100 symbols, and the start page has no search, sort or peoples marker"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: high
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-551]
refs: [viewer/index.html, viewer/zoom.html, viewer/start.js, docs/review/code-audit-2026-10/img/, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. Three things greet you with the least useful view. A peoples run opens at its first moment, 20 million years ago, when there are no peoples, so the peoples map is grey and says "peopled 0% of the land". A regional zoom opens with waterfalls, volcanoes and 984 mineral deposits all switched on, burying the satellite picture. And the start page lists 59 cards in creation order, named after test batches, with no search, sort, or sign of which ones have peoples (the thing you open most).

From the viewer-ux audit (zoom defaults verified: `zoom.html:114-119` `falls`, `volc`, `dep` are `checked`).

Fix:
- [ ] peoples runs open at the present (main runs stay at the start)
- [ ] zoom: only "Rivers and lakes" on by default; remember overlay choices in localStorage
- [ ] start page: search box, sort (newest, starred first, name), filter chips (has peoples, L7, starred), a "peoples" chip on cards (start.js:123 already builds chips)
- [ ] rename "All 1" to "Family (1)"; make Globe/List a true either-or

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-first-look-opens-where-the-interest-is.md (found by code-audit-2026-10).
