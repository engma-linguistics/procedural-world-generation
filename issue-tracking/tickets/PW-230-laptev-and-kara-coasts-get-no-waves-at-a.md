---
id: PW-230
title: "Laptev and Kara coasts get no waves at all: a half-year at least half frozen blocks every ray"
type: task
status: done
parent: null
subsystem: coast
effort: s
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-075]
refs: [planet/coast.py, tools/coast_check.py]
created: 2026-10-15
updated: 2026-10-16
---

## Description
tools/coast_check.py: Laptev (Lena delta) and Kara (Ob/Yenisei gulfs) wave power 0.0 kW/m (obs ~0.3-3, open water Jul-Sep only). coast.wave_power_winds blocks a ray at any cell frozen for >= half of the half-year (`blocked = icy >= 0.5`), and the Apr-Sep half-year is mostly frozen there, so both half-years are blocked and the coast gets nothing, though its sea is open and wave-making for ~3 months. Fix: per half-year, scale each stretch's growth by its open share instead of a hard block (or treat the open months as their own short season), keeping the arriving power scaled by the coast cell's open share as now.
- [ ] Laptev and Kara in 0.3-3 kW/m; Beaufort and the other rows unchanged

## Updates
- 2026-10-16: Status in-progress -> done. Coast side done: wave power summed over the coast's open season. Laptev/Kara still 0 because their coast cells never thaw in the climate (warmest month -2.1/-3.1 C vs obs 4.9/2.5): merged into the frozen-sea summer air ticket.
- 2026-10-16: Coast batch: the hard block (icy >= 0.5) is replaced by an integral over the coast's open season. The sine ice model's open windows nest round the warm peak, so at each moment the open sea is the cells open longer than x (3-point Gauss-Legendre; test_wave_short_open_season). Laptev and Kara stay at 0.0 kW/m, but that isn't the rays: their coast cells are frozen all year because the climate's warmest month there is -2.1 / -3.1 C (observed 4.9 / 2.5; Arctic coastal sea median -1.2 vs 2.7, 47% never thaw). With +3 C over the Arctic sea as a diagnostic they get 5.4 / 4.5 kW/m. Beaufort 6.8 -> 7.3. Remaining cause in the climate: draft draft-arctic-coastal-sea-summers-too-cold.md.
- 2026-10-15: Status todo -> in-progress. Coast batch agent started.
- 2026-10-15: Created from inbox draft draft-arctic-waves-ice-blocked.md (found by smalls2).
