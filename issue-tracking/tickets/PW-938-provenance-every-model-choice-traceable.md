---
id: PW-938
title: "Provenance: every model choice traceable to its sources, including what was tried and dropped"
type: epic
status: todo
parent: null
milestone: v2
subsystem: docs
effort: xl
impact: high
found_by: owner
blocked_by: []
relates: []
refs: [docs/review/assumptions-audit/findings.json]
created: 2026-10-27
updated: 2026-10-29
---

## Description
Owner 2026-10-27: bury doubters under evidence. Cite specific sources in code, the wiki and commit messages. Record what was tried and didn't work, and why the adopted approach did.

Ground rules:
- Every citation is verified (author, year, title, DOI or URL) before it lands. A wrong citation is worse than none.
- Unverifiable claims are marked "uncited: our estimate" rather than guessed.
- Git history is never rewritten. Old commits are covered by a provenance ledger, not amended.
- There are about 99 distinct inline author-year citations in planet/ today, unverified and in no central registry.

## Updates
- 2026-10-29: Owner 10-29: provenance moves to v2 in its entirety.
- 2026-10-27: Created from inbox draft draft-provenance-epic.md (found by owner).
