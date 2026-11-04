---
id: PW-1208
title: No tool scores waves and tides on Earth any more; docs/overview.md section 2.10 still quotes old waves and tides counts
type: task
status: todo
parent: null
milestone: later
subsystem: coast
effort: s
impact: low
found_by: lane88-docs
blocked_by: []
relates: [PW-816]
refs: [tools/coast_check.py, docs/overview.md, README.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
While regenerating overview section 3 (PW-816) I found that `tools/coast_check.py` no longer scores waves or tides.
It now scores coast form on the Earth world (21 of 32 named places right on 2026-10-31) plus the coast classes'
lengths. The older numbers ("waves within 2x at 25 of 32 coasts, tides within 2x at 24 of 25", overview section 2.10)
came from an earlier version of the tool. The README claim was removed, and section 2.10 now says the figure is dated
2026-10-16 and not regenerated. Nothing checks wave power or tide range against observed coasts, so a change to
`coast.py` can drift unnoticed.

Options: restore a waves-and-tides scorer (named coasts with observed wave power and tide range, from git history
before the coast form rewrite) as `tools/wave_tide_check.py`, run it on the Earth world, and put its numbers in section
3. Earth stays a plausibility anchor; this is a regression guard, not a fit target.
- [ ] a tool that prints waves and tides against named observed coasts
- [ ] overview section 2.10 and section 3 quote its output, dated

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: coast detail polish
- 2026-10-31: Created from inbox draft draft-waves-tides-check-tool.md (found by lane88-docs).
