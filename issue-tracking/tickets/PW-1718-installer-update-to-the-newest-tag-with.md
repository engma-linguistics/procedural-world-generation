---
id: PW-1718
title: "Installer: update to the newest tag with rollback, an 'update available' note in the viewer, and an uninstall that asks about the data"
type: task
status: done
parent: null
milestone: v1.0
subsystem: infra
effort: m
impact: med
found_by: plan-v1-lane
blocked_by: []
relates: []
refs: [docs/review/plan/milestones-to-v1.md, planet/server.py, viewer/index.html, docs/coordination.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: once installed, you can update with one command or from the viewer, go back if the update is bad, and remove the program without losing your worlds unless you say so.

If it is never done, every new tag means a manual reinstall, and a bad update has no way back. Uninstalling leaves uv's private Python and the launchers behind.

- `procgen-world update`: fetch the newest tag into a new `app/<version>`, run `uv sync --frozen`, run a smoke check (the server starts, `/viewer/` loads), then switch `current`. Keep the previous version.
- `procgen-world rollback`: switch `current` back to the previous version.
- The project has no backward compatibility (docs/coordination.md), so the update notes say whether existing runs still open.
- The start screen shows "update available" with the notes (owner-facing, so it lives in the viewer).
- `procgen-world uninstall`: remove the app folders, uv's private Python, the launcher, the .desktop entry and the config. Ask separately about the data folder, show its size, and keep it by default.

- [ ] Update, rollback and uninstall each work on a test install, with the data folder byte-identical before and after

## Updates
- 2026-11-11: Status todo -> done. merged (lanes 304/306)
- 2026-11-11: Created from inbox draft draft-installer-update-uninstall.md (found by plan-v1-lane).
