---
id: PW-922
title: Tickets still cite planet/lineages/history.py, which is now a package
type: task
status: todo
parent: null
milestone: null
subsystem: docs
effort: xs
impact: low
found_by: pw901-history-split
blocked_by: []
relates: [PW-901]
refs: [planet/lineages/history/, issue-tracking/tickets/, docs/review/backlog-workgroups/proposal.md]
created: 2026-10-27
updated: 2026-10-27
---

## Description
PW-901 turned `planet/lineages/history.py` into the package `planet/lineages/history/`
(`model.py`, `steps.py`, `habitat.py`, `dispersal.py`, `competition.py`, `contact.py`,
`origins.py`, `peoples.py`, `portals.py`, `pressure.py`, `summary.py`, `tags.py`, `tries.py`,
`events.py`, `frame.py`, `groups.py`, `params.py`, `gridops.py`). Older tickets were left as
they were, so 40 ticket `refs` lists (25 of them done or wontdo) and one more ticket
Description still name `planet/lineages/history.py`, as do
`docs/review/backlog-workgroups/proposal.md` and `docs/review/assumptions-audit/findings.json`.
`board.py check` does not flag them (it only checks run/world/zoom ids), but a reader following
the ref finds no file.

Find them with `grep -l "lineages/history.py" issue-tracking/tickets/*`. For each open ticket,
replace the ref with the module that now owns the code (or `planet/lineages/history/` where it
spans several). Leave done/wontdo tickets and the review docs alone, or add one Updates line
saying the file became a package; Updates are append-only, so do not rewrite old entries.
- [ ] open tickets' refs point at existing paths
- [ ] `grep -l "lineages/history.py"` finds only closed tickets and dated review docs

## Updates
- 2026-10-27: Created from inbox draft draft-repoint-history-py-refs.md (found by pw901-history-split).
