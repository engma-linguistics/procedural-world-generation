---
id: PW-942
title: "Provenance: a verified reference registry and citation convention, with a checker"
type: story
status: todo
parent: PW-938
milestone: later
subsystem: docs
effort: m
impact: high
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-27
updated: 2026-11-03
---

## Description
- docs/references.md (or .bib) holds one entry per source with a short key, full citation and DOI/URL, plus what we use it for.
- Code comments cite by key, e.g. `[Damuth1981]`.
- A tools/ check fails if a cited key is missing from the registry. Wire it into the board/test hooks.
- Write the convention into CLAUDE.md and docs/coordination.md, so every agent prompt carries it and commit messages cite keys too.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: provenance project is documentation, not needed for a stable planet or the culinary goal
- 2026-10-29: Owner 10-29: provenance moves to v2 in its entirety.
- 2026-10-27: Created from inbox draft draft-provenance-registry.md (found by owner).
