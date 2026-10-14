---
id: PW-128
title: "Viewer: show where each world/zoom/time zoom came from, and what each run has made"
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-091, PW-103]
refs: [viewer/index.html, viewer/zoom.html]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner: make it clearer which world came from which timeline. In the picker and the info panel, show each world as '<run name> @ T Myr' with a link back to the run at that time; for a run, list its worlds, zooms and time zooms (a small tree), and mark world times on the run's timeline slider. Step toward the one-grand-timeline view of PW-103.

## Updates
- 2026-10-14: Status todo -> done. worlds/index.json carries source_run/source_run_name/t_myr; world panel shows '<run name> @ T Myr' linked to the run at that time plus its zooms; run panel lists worlds (with zooms) and time zooms as a tree, ticks above the time slider (click: go there); picker labels worlds by provenance; zoom.html source line links '<run name> @ T Myr'.
- 2026-10-14: Created.
