---
id: PW-940
title: "Provenance: harvest and verify existing citations (code, wiki, decisions, tickets, git log)"
type: story
status: todo
parent: PW-938
milestone: v1
subsystem: docs
effort: l
impact: high
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-27
updated: 2026-10-29
---

## Description
- Collect every author-year mention in planet/, tools/, docs/, issue-tracking/ and `git log`.
- Verify each one against Crossref or the publisher's page (web lookup). Fix wrong ones, and mark unfindable ones.
- Convert the code mentions to registry keys.
- Report how many were confirmed, corrected and unverifiable.

## Updates
- 2026-10-29: 10-29 paper batch checked against the code: Nagy 1999 intercepts, McKenzie 1978 SAG constants, Burke & Dewey's 120 degrees and KJ_PER_G_LIVE (via Farlow 1993) are confirmed and their comments carry page or table; the Ripple 2014 'few percent' citation was wrong and is corrected (draft filed).
- 2026-10-27: Created from inbox draft draft-provenance-harvest.md (found by owner).
