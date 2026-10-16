---
id: PW-407
title: Run/world/zoom pickers need a type-to-filter box (ids, names)
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [viewer/index.html, viewer/zoom.html]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner: the planet viewer's dropdowns (runs, worlds, zooms) need a text box to type an id (e.g. b3c260) or part of a name and narrow the list. Apply to every picker in index.html and zoom.html; Enter opens the single match.

## Updates
- 2026-10-16: Status todo -> done. Done on branch worktree-agent-a3947a9de2078ba52: viewer/pickfilter.js adds a filter box above the run/world picker (index.html) and the zoom picker (zoom.html): words matched against id, label, title and group (a run id in the zoom picker lists its zooms), count shown, Enter opens the single match (several: drops the list open), Esc clears, a pick clears the filter. Exercised headless (98ee -> Enter opened run 98ee98; b3c260 in the zoom picker -> Enter opened it).
- 2026-10-16: Created from inbox draft draft-picker-filter.md (found by daniel).
