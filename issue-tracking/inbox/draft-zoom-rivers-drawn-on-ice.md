---
title: "Zoom viewer draws rivers across ice sheets"
type: task
status: todo
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: zoomice
blocked_by: []
relates: [PW-127]
refs: [viewer/zoom.html, planet/zoom.py, "zoom 516056", docs/review/ice/polar_516056_biome.png]
---

## Description
The landscape pass routes discharge under the ice (rightly: meltwater and the bed's drainage), and the zoom viewer's rivers overlay draws every channel above its threshold, so a polar ice sheet (zoom 516056, world 800c99 at 74,-178) is covered in blue river lines. Either don't draw rivers where `ice > 0` (start them at the snout) or draw them fainter as subglacial drainage. The zoom's own preview.png already hides them under the ice tint.
