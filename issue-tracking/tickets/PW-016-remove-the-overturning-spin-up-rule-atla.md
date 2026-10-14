---
id: PW-016
title: Remove the overturning spin-up rule; Atlantic on and Pacific off by themselves
type: story
status: todo
parent: PW-013
subsystem: ocean
effort: m
impact: high
found_by: ocean
blocked_by: [PW-015]
relates: []
refs: [planet/ocean.py, docs/proposals/ocean_overturning.md]
created: 2026-10-14
updated: 2026-10-14
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
- 2026-10-14: Created from the rain/overturning epic. Merged: Known issue 'The North Atlantic's on-state is found by a spin-up rule' and the Earth AMOC 11 vs 17 Sv figure (ocean), morning decision 3(a).
