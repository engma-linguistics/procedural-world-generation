---
id: PW-562
title: "Ice-onset check (low-latitude ice only after high-latitude ice) needs a height cut: tropical plateau ice trips it on every run"
type: task
status: todo
parent: PW-470
milestone: later
subsystem: timezoom
effort: xs
impact: low
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555]
refs: [planet/tectonics/diag.py, tools/ice_criteria.py]
created: 2026-10-22
updated: 2026-10-23
---

## Description
The N5 check (Chandler & Sohl 2000: low-latitude ice only after high-latitude ice) in tools/ice_criteria.py reads
diag.py's lowest iced latitude, which on main is the high tropical plateaus' ice (below 30 deg on 28-56% of climate
updates, at any dT; even at dT +16 in the hysteresis probe). Record the lowest latitude of ice whose bed is below
~1000 m (sheet ice, not mountain caps) in diag.py and use it in the check. Also: the run keeps 1-4% of its land iced
on plateaus at every dT it reaches; whether that much tropical high ice is right is worth a look (Earth's tropical
glaciers are ~0.003% of land).

## Updates
- 2026-10-23: Milestone v1 -> later (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-onset-check-height-cut.md (found by ice-v2-stage0).
