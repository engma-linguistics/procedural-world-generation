---
id: PW-181
title: "Zoom: waterfall marks are unlabelled white specks baked into the preview; make them a toggleable, hoverable overlay"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-120, PW-150]
refs: [planet/zoom.py, viewer/zoom.html, "zoom:2d06f8"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner asked what the white round specks in zooms are (e.g. zoom 2d06f8). They are waterfall marks: zoom.preview paints a white-water blob at every listed fall (stats.falls, >= 30 m since PW-150), radius growing with height. Unlabelled and baked into the image, they read as noise. Draw falls in zoom.html as an overlay instead (toggle 'Waterfalls', a small marker plus hover/click card with height, discharge, kind, gorge length, cascades), keep the preview clean (or keep a subtle mark only for the top few), and add a legend line.

## Updates
- 2026-10-14: Created.
