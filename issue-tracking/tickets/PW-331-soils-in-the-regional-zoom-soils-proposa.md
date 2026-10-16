---
id: PW-331
title: "Soils in the regional zoom (soils proposal step 6): per-pixel passes around the zoom vegetation"
type: task
status: in-progress
parent: PW-184
subsystem: zoom
effort: m
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-185, PW-214]
refs: [docs/proposals/soils.md, planet/soils.py, planet/zoom_vegetation.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Step 6 of docs/proposals/soils.md: run soils' mineral pass per zoom pixel on the zoom's own slope, rivers, ice and
landforms before the zoom vegetation (replacing `SOIL_THIN` / `DEEP_SOIL`), and the organic pass after it; zoom soil
layers, viewer legend. World soils (steps 1-5, 8) are in `planet/soils.py` (PW-185).

## Updates
- 2026-10-16: Status todo -> in-progress. Agent started.
- 2026-10-16: Created from inbox draft draft-zoom-soils.md (found by coordinator).
