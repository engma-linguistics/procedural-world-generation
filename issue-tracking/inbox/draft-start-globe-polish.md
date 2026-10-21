---
title: Start-page globe picker polish (drag to rotate, lighting, higher-res texture)
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: pw546
blocked_by: []
relates: [PW-546]
refs: [viewer/globepick.js, planet/thumbs.py]
---

## Description
PW-546 shipped the globe picker with a flat-shaded sphere (MeshBasicMaterial), automatic rotation only, and a 1024x512 biome/elevation texture from `/api/thumb?proj=equirect&w=1024`. Possible follow-ups: drag to spin and pause the auto-rotation, a light and terminator so it reads as a planet, an atmosphere rim, pause rotation when the tab is hidden (already done) or when `prefers-reduced-motion` is set, and a 2048 texture option. Also: stale pre-PW-546 files in `<data root>/.thumbs/` named `<kind>-<id>-<mtime>.png` are only removed when that item's thumbnail is next drawn; a one-off sweep would clear the rest.
- [ ] honour `prefers-reduced-motion` (no auto-rotation)
