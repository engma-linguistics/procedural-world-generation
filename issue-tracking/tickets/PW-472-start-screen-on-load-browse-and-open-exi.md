---
id: PW-472
title: "Start screen: on load, browse and open existing runs, worlds and zooms, or make a new planet with a settings form"
type: story
status: todo
parent: PW-244
subsystem: viewer
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-248]
refs: [planet/viewer/index.html, planet/server.py, planet/api.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
Owner 2026-10-20. When the viewer opens, it shows a start screen instead of dropping into the last run.
- Gallery of existing planets (runs) with thumbnails, seed, level, length and date. Each opens its run, worlds and zooms. Delete with a confirm.
- 'New planet': a form for the variables a user should set, each with sensible defaults and a short explanation:
  - seed (with a random button) and grid level (6 quick, 7 showcase);
  - length in Gyr and a preset (earthlike, plus any that exist);
  - planet settings the run already supports, such as orbit, sun or land fraction. Only expose what the code honours: list what is configurable today and flag the gaps as drafts.
  - Submitting starts a job with progress and an estimated time, from the run-cost table in docs/coordination.md.
- Uses PW-248's one-command chain (planet make) for the full seed-to-finished-world flow, with checkboxes for the optional stages (time zoom, finishing, highlights, zooms). PW-248 can be built with or before this.
- Works at phone width; no backward compatibility with old stores needed.

## Updates
- 2026-10-20: Built on branch worktree-agent-a37d9b944587e6d92 (not merged): viewer/start.js (gallery of planets with thumbnails, seed/level/length/date, open, family list, delete with confirm; New planet form with presets, seed + random, level 5/6/7, length, stage checkboxes, the 7 tectonics settings the code honours, live time estimate, job progress that survives a reload), planet/family.py (/api/planets), planet/thumbs.py (/api/thumb). Checked in headless Chrome at 1200 and 390 px. Configurable today: n_plates, start, continental_fraction, continental_start, heat_start, tilt, climate_offset; gaps in draft-make-settings-gaps. Other drafts: viewer-phone-layout (the old globe UI), make-resume-cancel.
- 2026-10-20: Created.
