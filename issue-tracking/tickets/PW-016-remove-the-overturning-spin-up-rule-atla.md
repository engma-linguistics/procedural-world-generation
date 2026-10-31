---
id: PW-016
title: Remove the overturning spin-up rule; Atlantic on and Pacific off by themselves
type: story
status: todo
parent: PW-013
milestone: v2
subsystem: ocean
effort: m
impact: high
found_by: ocean
blocked_by: [PW-015]
relates: []
refs: [planet/ocean.py, tools/moisture_budget.py, docs/review/audit/pw015-rain.md]
created: 2026-10-14
updated: 2026-10-31
---

## Description
`planet/ocean.py` finds the North Atlantic on-state with a spin-up rule (`moc_spin`: with no earlier
state, every polar sea that is nearly dense enough starts sinking, and the threshold tightens over the
iterations). Without it the model's own salinity leaves the Nordic seas too fresh to sink. Once
moisture transport is fixed, remove the rule and check that sinking starts in the Nordic/Labrador seas
and not in the North Pacific from salinity alone.

Also in scope: Earth gives ~11 Sv of North Atlantic sinking against an observed AMOC of ~17 Sv; and
there's no lasting off-state (after ~1 Sv hosing it recovers within 2–3 climate updates; see PW-018).

## Updates
- 2026-10-31: Lane 98 (PW-1229): the L7 pass on this bar (>= +0.25 Sv) was an artefact; the Amazon mouth cell and Ob gulf were cut-off 'seas' so 7.5 Mkm2 of Atlantic catchment was missing. Corrected: Atlantic E-P-R +0.12 Sv at L7, +0.08 at L6; Atlantic minus Pacific -55 mm/yr.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Milestone null -> v1 (PW-597 triage, coordinator, 2026-10-23): rain is v1; the owner put sim-physics work back under v1 on 2026-10-22.
- 2026-10-16: Merged inbox draft draft-pw016-spin-up-status.md ("PW-016 after PW-015 stages 1-2: the spin-up rule is already inert on Earth, but the Atlantic's catchments are still too wet (E-P-R +0.20 Sv at L6)", found by pw015-rain).
  For PW-016 (probably `--merge-into PW-016`). Tried at the end of the PW-015 lane:
  - Earth L6 and L7 give the same overturning with `moc_spin` 6 (default), 1 (no spin-up), 30 or 0.5: 14.6
    Sv, 13.7 in the Nordic seas, none in the Labrador sea or the North Pacific (L7 14.5 / 13.8); so on main
    too (13.8 / 11.3). Since PW-360 the solver iterates to a steady state, which forgets how it started.
  - On generated worlds' terrain it still picks between steady states on some: world bd9a7a 29.6 -> 26.9 Sv
    without it (its 66N 116E site moves to 62N 84E); 592f2a, 3f6a76, fac2af within 0.3 Sv.
  - The proposal's condition (section 7: Atlantic E-P-R >= +0.25 Sv and >= 100 mm/yr above the Pacific, at
    L6 and L7) isn't met: L6 +0.20 Sv, -16 mm/yr (main +0.06, -26). E - P is right-signed and large (Atlantic
    1.60 Sv vs NCEP E - GPCP P 1.13), but the Atlantic's rivers return 1.40 Sv (Dai & Trenberth ~0.55): the
    Amazon (3755 mm vs 2335), Congo and Sahel catchments are too wet. L7's +0.71 Sv is the budget tool's
    routing, not the model (draft-moisture-budget-l7-drainage).
  So the rule can go only after the tropical land dries (PW-015 stage 3+, behind PW-352); or decide that a
  rule which only selects between steady states is acceptable.
- 2026-10-14: Created from the rain/overturning epic. Merged: Known issue 'The North Atlantic's on-state is found by a spin-up rule' and the Earth AMOC 11 vs 17 Sv figure (ocean), morning decision 3(a).
