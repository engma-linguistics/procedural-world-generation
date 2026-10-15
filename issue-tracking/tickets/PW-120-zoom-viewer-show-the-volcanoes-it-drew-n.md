---
id: PW-120
title: "Zoom viewer: show the volcanoes it drew (name, age, form) on hover or as markers"
type: task
status: done
parent: PW-001
subsystem: viewer
effort: s
impact: low
found_by: volcanoes
blocked_by: []
relates: [PW-004]
refs: [viewer/zoom.html, planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Each zoom's `zoom.json` now lists the volcanoes it drew under `stats.volcanoes` (kind, form such as
"atoll", "island with a barrier reef", "guyot", age in Myr, summit height, x/y km from the centre).
`viewer/zoom.html` doesn't show them. Small markers (or a hover line: "atoll, 18 Myr old, sunk 230 m")
would make chains readable: which island is the youngest, which seamount is a drowned atoll.
- [ ] Markers or hover text from `stats.volcanoes` in zoom.html

## Updates
- 2026-10-14: Status todo -> done. Volcanoes overlay in zoom.html from stats.volcanoes: ▲ red active / brown extinct / hollow blue below the sea, sized by height; card with form, kind, active or age, summit above/below the sea, height; zoom_volcanoes adds active. docs/review/zoom/130acd_relief_volcano.jpg (zoompolish).
- 2026-10-14: Created from inbox draft draft-zoom-volcano-markers.md (found by volcanoes).
