---
id: PW-229
title: How strong should the vegetation's climate feedbacks be? (now conservative nudges)
type: task
status: done
parent: null
subsystem: climate
effort: xs
impact: low
found_by: vegclim
blocked_by: []
relates: [PW-203]
refs: [planet/climate.py, planet/vegetation.py, docs/proposals/vegetation.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-203 added all three feedbacks (owner decision 6B) as nudges referenced to Earth's land means, so Earth moves little: Budyko w 2.2-3.3 (5-95%), rain recycling et 0.4-0.6, albedo nudge typically +-0.5 C per half-year (98% within -0.5..+0.6 C; cap 2 C). Coupled loop is stable (slightly damping) even at doubled gains.

The albedo nudge uses a local sensitivity of 0.03 C per W/m2 (`albedo_k`) and half-year means, so the boreal forest's famous spring warming (dark trees over snow; several C in April-May in reality) shows only as ~+0.2 C in the 50-70 N summer half-year. Options:
- A) keep as is (lean): a nudge, Earth calibrated, no runaway risk; worlds differ mostly before land plants (bare continents: less recycling, more runoff, hotter dry summers).
- B) double `albedo_k` (0.06) and `et_band` (0.3): visible treeline sharpening and wetter forested interiors on generated planets; Earth's global numbers barely move, regional ones a little (not checked in detail).
- C) per-month albedo effect on the coldest/warmest-month temperatures (needs month-resolved temperatures; bigger change).

## Updates
- 2026-10-15: Status needs-decision -> done. Coordinator decision (north star, 'nudge, don't force'): keep the conservative gains. Earth means are calibrated and stable; raise them only if a later Earth check shows the vegetation-climate coupling too weak (e.g. Amazon/Sahel recycling).
- 2026-10-15: Created from inbox draft draft-veg-feedback-strength.md (found by vegclim).
