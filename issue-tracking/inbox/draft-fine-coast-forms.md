---
title: Fine-zoom shore has no explicit beaches, cliffs or coast-slope-driven inlets
type: task
status: todo
parent: null
milestone: later
subsystem: zoom
effort: m
impact: low
found_by: pw488-coast
blocked_by: []
relates: [PW-488, PW-392]
refs: [planet/zoom_fine.py, tools/coast_steps.py, "zoom 24584e", "zoom 1b331e"]
---

## Description
PW-488 draws the fine shore by sampling the parent's ground through a fractal displacement near its coast (zoom_fine.COAST_PX, 0.38 parent px), so the outline is fractal and unstaircased with bays, headlands and a few islets. The displacement is the same on every shore, whatever its slope or rock: a steep rocky coast and a flat sandy one get the same roughness, and there are no explicit beach ridges or cliffs beyond what zoom_coastal.shoreface already gives. Idea: scale the displacement by the local shore slope and rock (rougher and more inlets on drowned hard-rock coasts such as the Norwegian one, smoother on soft shores), and place beaches/cliffs on the new coast from the same inputs.
- [ ] displacement amplitude varies with shore slope and rock
- [ ] beaches on gentle shores and cliffs on steep ones at the fine pixel
