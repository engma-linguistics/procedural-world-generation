---
id: PW-027
title: "Arctic coasts: sea-ice damping of waves and tides"
type: task
status: todo
parent: null
subsystem: coast
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-028]
refs: [planet/coast.py, "zoom f81832", "world 0f7abd", tools/coast_check.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Arctic coasts should get much lower wave power (sea ice covers them most of the year) and so lean
river-dominated deltas. Tides on Arctic shelves are also too big (no sea-ice damping). Scale wave power
(and tidal range) by the ice-free season from the world's temperature/sea-ice. Reference: zoom f81832 on
world 0f7abd, a Lena-like river (2.2 Mkm² basin, −12 °C mean, 16,800 m³/s) that comes out
wave-dominated.

## Updates
- 2026-10-14: Created from the owner discussion 2026-10-14. Merged the Arctic part of Known issue 'Tides: Arctic shelves too big' (deltas).
