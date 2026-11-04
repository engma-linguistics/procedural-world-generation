---
id: PW-523
title: Fine-zoom shore has no explicit beaches, cliffs or coast-slope-driven inlets
type: task
status: todo
parent: PW-516
milestone: later
subsystem: zoom
effort: m
impact: low
found_by: pw488-coast
blocked_by: []
relates: [PW-488, PW-392]
refs: [planet/zoom/fine.py, tools/coast_steps.py, "zoom 24584e", "zoom 1b331e"]
created: 2026-10-21
updated: 2026-11-03
---

## Description
PW-488 draws the fine shore by sampling the parent's ground through a fractal displacement near its coast (zoom_fine.COAST_PX, 0.38 parent px), so the outline is fractal and unstaircased with bays, headlands and a few islets. The displacement is the same on every shore, whatever its slope or rock: a steep rocky coast and a flat sandy one get the same roughness, and there are no explicit beach ridges or cliffs beyond what zoom_coastal.shoreface already gives. Idea: scale the displacement by the local shore slope and rock (rougher and more inlets on drowned hard-rock coasts such as the Norwegian one, smoother on soft shores), and place beaches/cliffs on the new coast from the same inputs.
- [ ] displacement amplitude varies with shore slope and rock
- [ ] beaches on gentle shores and cliffs on steep ones at the fine pixel

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: fine-zoom or coast-form polish; zooms read well enough
- 2026-10-21: Created from inbox draft draft-fine-coast-forms.md (found by pw488-coast).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
