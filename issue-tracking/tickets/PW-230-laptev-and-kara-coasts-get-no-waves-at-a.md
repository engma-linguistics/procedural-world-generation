---
id: PW-230
title: "Laptev and Kara coasts get no waves at all: a half-year at least half frozen blocks every ray"
type: task
status: todo
parent: null
subsystem: coast
effort: s
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-075]
refs: [planet/coast.py, tools/coast_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
tools/coast_check.py: Laptev (Lena delta) and Kara (Ob/Yenisei gulfs) wave power 0.0 kW/m (obs ~0.3-3, open water Jul-Sep only). coast.wave_power_winds blocks a ray at any cell frozen for >= half of the half-year (`blocked = icy >= 0.5`), and the Apr-Sep half-year is mostly frozen there, so both half-years are blocked and the coast gets nothing, though its sea is open and wave-making for ~3 months. Fix: per half-year, scale each stretch's growth by its open share instead of a hard block (or treat the open months as their own short season), keeping the arriving power scaled by the coast cell's open share as now.
- [ ] Laptev and Kara in 0.3-3 kW/m; Beaufort and the other rows unchanged

## Updates
- 2026-10-15: Created from inbox draft draft-arctic-waves-ice-blocked.md (found by smalls2).
