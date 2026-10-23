---
title: The 2026-10-21 v2 proposal's milestone moves, merges and drops were never applied to the board
type: task
status: needs-decision
parent: null
subsystem: docs
effort: s
impact: med
found_by: docs-cleanup
blocked_by: []
relates: [PW-244]
refs: ["git d32f7fa:docs/review/v2-proposal.md (deleted 2026-10-23)", "git d32f7fa:docs/review/v1-reassessment-2026-10-16.md"]
---

## Description
`docs/review/v2-proposal.md` (read-only review prepared 2026-10-21, deleted in the 2026-10-23 docs cleanup; recover with `git show d32f7fa:docs/review/v2-proposal.md`) proposed milestone moves, merges and drops that the board does not yet reflect (checked 2026-10-23: the tickets named below still have the old status/milestone). The board is now the source of truth, so the proposal was deleted. Its still-open recommendations, for the owner to accept or reject in one pass:

**Close / merge / supersede**
- PW-432 into PW-054 (evidence for it, not separate work).
- PW-498 into PW-202 (v1 showcase remake).
- PW-033 into PW-448 (same Earth time-zoom glacial depth gap).
- PW-332 into PW-313 (same Antarctic snow gap).
- PW-115 superseded by PW-460 (margin melt; PW-460 is the fix).
- PW-219 into PW-481 (planet form) if the planet-settings work covers other sizes.
- PW-421: close after the PW-366 re-measure. PW-417: close if the owner's Chrome test of PW-415 is done.
- Wontdo candidates: PW-443 (weird worlds), PW-368 (parked drift), the Earth-only misses PW-152, PW-324, PW-325.

**Move into v1** (real bugs in v1 features): PW-508 (make-job restart redoes the tectonic simulation), PW-446 (cached mantle basis differs from a fresh build), PW-348 (sub-0.5 m land stored as sea but carries soil and vegetation), PW-503 (humanuse on a zoom builds edge lists for every pixel).

**Move to later:** the ice subtree PW-470 (see `board.py tree --open` for its children), PW-103, PW-490, PW-156, PW-207, PW-494.

**Existing v1 items to re-check:** PW-284 (flexural moat 15% share tuned on one seed's closed-basin count; metric-chasing per the audit rule) and PW-304 (rain kernel vapour not mass-conservative; a real v1 bug, prioritise).

**Open owner decisions it listed:** (1) is rain (PW-015/016) v1 or v2; (2) soils in v1 (PW-212/330) or v2 with coastal life (PW-097); (3) PW-206 vs PW-475: game attributes are not v1 but game export is, pick one (both are v2 today, so likely moot); (4) confirm PW-470 and children move to later; (5) the wontdo list above. Also PW-502 (fjord harbours) v1 or v2.

Options: A) accept all and apply with `board.py update`; B) go through them selectively; C) drop the lot as overtaken by events. Lean: B, starting with the merges (cheap) and the four v1 bug moves.

- [ ] each item above applied or explicitly rejected
