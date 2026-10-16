---
id: PW-315
title: Cell detail panel - a 12-month climograph (worlds store monthly temperature and rain)
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: low
found_by: viewer-replay-speed
blocked_by: []
relates: [PW-194]
refs: [viewer/index.html, planet/climate.py, planet/world.py, planet/store.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The viewer's "More detail" panel (cell info, `seasonChart` in viewer/index.html) draws a small chart from
what a world stores: January / year / July temperature with the coldest-to-warmest-month range, and the
two half-year rain rates. A proper climograph (12 monthly temperature points and rain bars) would read
better for travel and climate checks, but worlds don't store months: `climate.months` (PW-194)
rebuilds them in Python from temperature, warm/cold month, the half-year rain, latitude and tilt.

Options: (A) a world stores `temperature_months` / `precipitation_months` (12 x cells, int8 / uint16 with
the store's scale; ~4-5 MB more at L7) from `climate.months`, and the panel plots them; (B) the viewer
asks the server for one cell's months (`GET /api/cell?world=&i=`, calling `climate.months` on that cell);
(C) port the month builder to JS (duplicated physics, would drift). Lean: B (no storage, exact, cheap).
- [ ] the panel shows 12 months of temperature and rain for world cells
- [ ] runs keep the current chartless panel (their keyframes don't carry the inputs)

## Updates
- 2026-10-15: Status in-progress -> done. Done (c1e3b2d): GET /api/cell (12 months from climate.months, ~7 ms warm) and a climograph in More detail for world cells.
- 2026-10-15: Status todo -> in-progress. Agent started (viewer follow-up).
- 2026-10-15: Created from inbox draft draft-viewer-cell-climograph.md (found by viewer-replay-speed).
