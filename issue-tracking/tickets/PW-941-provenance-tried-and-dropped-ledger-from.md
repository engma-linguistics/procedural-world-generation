---
id: PW-941
title: "Provenance: tried-and-dropped ledger from git history and review docs"
type: story
status: todo
parent: PW-938
milestone: v2
subsystem: docs
effort: l
impact: med
found_by: owner
blocked_by: []
relates: []
refs: [docs/review]
created: 2026-10-27
updated: 2026-10-27
---

## Description
Build docs/wiki/tried-and-dropped.md by mining git log, docs/review/* and closed tickets. For each entry:
- what was tried, with its source;
- what happened (numbers);
- why it was dropped and what replaced it, with its source;
- the commit hashes.

Commits stay as they are; the ledger links them. Going forward, agents add entries when they drop an approach.

## Updates
- 2026-10-27: Created from inbox draft draft-provenance-ledger.md (found by owner).
