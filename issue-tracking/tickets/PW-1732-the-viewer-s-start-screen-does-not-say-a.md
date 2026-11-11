---
id: PW-1732
title: The viewer's start screen does not say an update is available
type: task
status: todo
parent: null
milestone: v1.0
subsystem: viewer
effort: s
impact: med
found_by: lane304
blocked_by: []
relates: []
refs: [install.sh, planet/appconfig.py, viewer/start.js, docs/review/plan/installer.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
`planet self update` and `planet self status` (install.sh) know the installed version and the newest release tag,
but the viewer does not. Daniel uses the viewer, not the CLI (plan §4, "Updates"), so an installed copy goes stale
silently and he will report bugs that the newest tag already fixed.

## Done when
- The server exposes the installed version and, at most once a day and only when online, the newest tag
  (`GET /api/version`; the install's `config.toml` or `install.env` says where the source is).
- The start screen shows "update available: vX → vY (planet self update)" and nothing when offline or up to date.

## Updates
- 2026-11-11: Created from inbox draft draft-viewer-update-available.md (found by lane304).
