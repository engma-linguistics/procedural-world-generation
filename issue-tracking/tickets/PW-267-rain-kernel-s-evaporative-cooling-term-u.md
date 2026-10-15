---
id: PW-267
title: Rain kernel's evaporative-cooling term uses mean_mm without the warm-world factor exp(0.03 dT)
type: task
status: todo
parent: PW-245
subsystem: climate
effort: xs
impact: low
found_by: audit-climate-ocean
blocked_by: []
relates: []
refs: [planet/climate.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`_rain` turns its running rain into mm/yr with `scale = mean_mm × S × n / tot` (climate.py:906), and uses that for the wet-cool / dry-hot correction `tcor` of shower instability. `compute` normalises the actual rain to `mean_mm × exp(0.03 dT)` (line 1832), but `rain()` passes the bare `tune["mean_mm"]`. At dT = ±10 the kernel's mm are off by ×1.35, which shifts `tcor` by up to ~0.3 °C. Fix: pass `mean_mm × exp(0.03 dT)`, for example by putting it in the tune dict `compute` hands to `rain()`. Outputs at dT = 0 are unchanged, so the golden tests should not move.

## Updates
- 2026-10-15: Created from inbox draft draft-audit-climate-ocean-tcor-wet-scale.md (found by audit-climate-ocean).
