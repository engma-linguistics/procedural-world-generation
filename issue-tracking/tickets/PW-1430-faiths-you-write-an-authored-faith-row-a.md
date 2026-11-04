---
id: PW-1430
title: "Faiths you write: an authored-faith row and an editor in the Religion tab"
type: task
status: done
parent: PW-1308
milestone: v2
subsystem: culture
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: Daniel writes in a faith (name, founding people or culture, place, year, named gods and domains, spreads or stays closed); it feeds the existing faith rules and rebuilds in seconds without re-running the peoples. Plan: docs/review/board/milestones-v2-v5.md.

## Updates
- 2026-11-03: Status todo -> done. Lane 166: Religion tab 'Your faiths' view (add, edit, remove); saved as the run's authored.json via POST /api/authored; gods.py splits derive into inputs() (the slow ~20-25 s land pass, kept in server memory) and replay() (~4-5 s at L7) so an edit or mode switch never re-runs the peoples. Authored faiths are founded under the faith rules at the first frame from their year on where the founder has gods; odd ones read out why not (tests/test_authored_faiths.py). Derived gods and taboos docs persist under <data root>/.godscache keyed by run, run.json mtime, mode and authored hash.
- 2026-11-03: Created.
