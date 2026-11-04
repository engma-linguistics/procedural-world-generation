---
id: PW-1118
title: The convergence lift (PW-1100) wets the subtropical heat lows' margins at 15-25 S, where the sinking-air mask is weak
type: task
status: todo
parent: PW-015
milestone: later
subsystem: climate
effort: s
impact: low
found_by: lane62
blocked_by: []
relates: [PW-1100, PW-1099]
refs: [planet/climate.py, docs/review/base-climate/moisture-inflow-ascent/]
created: 2026-10-30
updated: 2026-11-03
---

## Description
In plain words. The new "rain where the low-level wind converges" term (kept as a patch, docs/review/base-climate/moisture-inflow-ascent/) adds rain where
the land-sea inflow converges into a heat low. Over the summer deserts that ascent is shallow: the subtropics'
sinking air caps it and it shouldn't rain. The model holds it down with the zonal sinking-air belt (`sink`, centred
25 deg from the rain belt, 9 deg wide). That mask is weak on the deserts' equatorward margins, especially at 15-25 S
in the southern summer. So the term turns some semi-arid land humid there.

Measured (lane 62, Earth L6, main vs ascent alone; Koppen B area lost):
- southern Africa ~570k km2, northern Africa ~290k, Australia ~80k, S America ~150k (gained elsewhere ~280k);
- B share 25.2 -> 24.3% (Kottek 30.1).

What to try, without tuning the mask's width:
- (a) Cap the lift at the heat low's own depth. The inflow rises only to fetch_h, so it rains only what saturates
  within that lift, as the storm lift's rh_c x exp(-q_k LAPSE lift) does. This gate is per-cell physics, not a mask.
- (b) Let the trade inversion follow the sea temperature, rather than a zonal belt.
Check it once PW-1099's inflow depth has its coastal partner, since the term rides with that.
- [ ] with the ascent on, Earth's B share no lower than with it off

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: rain kernel is calibration polish and three strikes sends it to the back of the line (PW-1363)
- 2026-10-30: Owner 10-30 D11: moisture/monsoon-coast work parked for v2; an agent will find a downloadable drag source.
- 2026-10-30: Created from inbox draft draft-ascent-wets-subtropical-heat-low-margins.md (found by lane62).
