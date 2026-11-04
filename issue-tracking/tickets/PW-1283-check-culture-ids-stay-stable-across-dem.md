---
id: PW-1283
title: Check culture ids stay stable across demes re-cuts before languages v0 keys lects on them
type: task
status: todo
parent: null
milestone: v2
subsystem: culture
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** Languages v0 gives one lect per culture and stores pairs and histories by culture id. If re-cutting demes or re-running the cultures pass renumbers cultures, every lect record breaks. Check whether ids are stable across re-cuts; if not, make them stable (for example keyed by founding deme and frame). Prerequisite for languages v0 (proposal round 2 section 7).

## Updates
- 2026-11-03: Milestones 11-03: later -> v2: v2 must-have: stable culture ids, so the language worktree's lects can key on them
- 2026-11-03: Triage 11-03: v2 -> later: languages, polities, religion and owner's-world empires wait until food is done (fresh-eyes review, D44)
- 2026-11-01: Created.
