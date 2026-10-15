---
title: "Waves: the U^5 gust factor is applied to U, overstating fetch- and duration-limited seas ~1.5-1.6x"
type: task
status: todo
parent: PW-245
subsystem: coast
effort: s
impact: med
found_by: audit-coast-zoom
blocked_by: []
relates: [PW-074, PW-075]
refs: [planet/coast.py, tools/coast_check.py, docs/review/audit/coast-zoom.md]
---

## Description
`GUST = 1.43 = 6.1^(1/5)` (coast.py:124-127) is the Weibull k=2 ratio E[U^5]/Ū^5, right for a fully developed sea.
But `_season_winds` multiplies U by it before the growth law. In this code, fetch-limited power goes as
U^(7/3) F^(4/3) and duration-limited (T_STORM) power as U^3. The correct power ratios are 1.43 and 1.91, but
the code gives 2.30 and 2.92: limited seas are overstated 1.61x (fetch) and 1.53x (duration) relative to
fully developed trade seas. Mid-latitude storm seas are duration-limited (15 m/s: 191 km duration limit vs
504 km full fetch). So the storm belts and enclosed seas are inflated relative to the trades, and
U_TRADE/U_STORM absorb part of it.

Fix (simplest sound): drop GUST and average the ray power over ~5 Weibull speed quantiles per season (U x
{0.42, 0.75, 1.0, 1.28, 1.75}-style nodes with equal weights), or apply the regime's moment ratio inside
the growth step. Then refit U_TRADE/U_STORM once on coast_check's open-ocean rows (together with the
L_RECOVER draft).
- [ ] no U^5-only factor on U; coast_check rows reported before and after
