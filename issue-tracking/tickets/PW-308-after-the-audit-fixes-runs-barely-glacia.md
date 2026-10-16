---
id: PW-308
title: "After the audit fixes, runs barely glaciate: 1 Gyr deepest ice sea level -9..-48 m on 11 seeds (Earth's icehouses ~-120 m)"
type: task
status: todo
parent: PW-244
subsystem: climate
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-240, PW-264, PW-265, PW-266, PW-275, PW-276, PW-277, PW-278]
refs: [docs/review/after-audit-2026-10-15/health/report.md, docs/review/health/2026-10-15/report.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The post-audit 1 Gyr health sweep (main cd9968b, 8 L6 + 3 L7 seeds, docs/review/after-audit-2026-10-15/health/) shows the
cold-era problem (PW-240) swung the other way. The deepest run ice sea level over 1 Gyr is now -9 to -48 m on every
seed, where the first sweep (docs/review/health/2026-10-15/, before the fixes) had -96 to -384 m. Median ice
covers 0.2-1.1% of the surface, and global temperature medians are 14.0-16.6 C (before 12.8-16.7, about the same).
Earth's last Gyr had ~4 icehouse intervals (Cryogenian, Andean-Saharan, Karoo, late Cenozoic), with ~-120 m at the
last glacial maximum and ~3% of the surface iced today. A showcase cold-era time zoom like 080df3 (-128 m at 126 kyr)
wouldn't happen on the current code.

Similar temperatures with much less ice point at the ice changes, or at their combination with the climate changes,
rather than at a warmer planet:
- the ice agent's health --quick, after PW-274..277 alone: s11 -247 m, s42 -124 m;
- the climate agent's, on the merged code (ice + climate): -71 / -15 m;
- now: <= -48 m.
Candidates: PW-277's one ice-surface climate (ice surfaces warmer than with the old 10 C cooling, so more melt);
PW-276's thinner caps on high ground (less high, cold ice to seed sheets); PW-275 (bare ground no longer damped);
PW-264/PW-278 (a weaker, slower weathering thermostat damps CO2 swings, and with them the cold eras).

To do: bisect on 2-3 L6 seeds (11, 42, 2; 1 Gyr) by reverting each change in turn, and find which process now
stops ice sheets from growing. Fix it soundly: no ice-growth fudge. The target isn't a number, but a 1 Gyr Earth-like
run should have some icehouse spells.

## Updates
- 2026-10-15: Created from inbox draft draft-runs-rarely-glaciate.md (found by coordinator).
