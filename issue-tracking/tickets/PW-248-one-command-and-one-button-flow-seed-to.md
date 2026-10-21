---
id: PW-248
title: "One-command and one-button flow: seed to finished world with sensible defaults"
type: story
status: done
parent: PW-244
subsystem: viewer
effort: m
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-10-15
updated: 2026-10-21
---

## Description
Today: simulate, slice (--at auto), highlights, zooms, timezoom, finish are separate steps. V1 wants one CLI command (e.g. planet make --seed N [--preset earthlike]) and a viewer 'New planet' button that runs the chain with job progress, picks a representative moment, optionally runs the time zoom to a glacial or interglacial 'now', finishes the world, computes highlights and a few zooms.

## Updates
- 2026-10-21: Status todo -> done. Merged 2026-10-20 (coordinator); follow-ups PW-478..483.
- 2026-10-20: Built on branch worktree-agent-a37d9b944587e6d92 (not merged): `planet make` (planet/make.py: simulate, representative moment, optional time zoom, finished world, highlights, N zooms; presets = the showcase recipes; `--dry-run` prints the plan and estimate) and `POST /api/make` as a server job with weighted progress (+ GET /api/make/options, /api/make/estimate). tests/test_make.py. Drafts: make-glacial-now (needs-decision), make-resume-cancel, make-estimate-calibration.
- 2026-10-15: Created.
