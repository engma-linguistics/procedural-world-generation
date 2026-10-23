---
id: PW-025
title: Supercontinent cycle regularity (pinned)
type: task
status: todo
parent: PW-649
milestone: later
subsystem: tectonics
effort: l
impact: low
found_by: mantle
blocked_by: []
relates: []
refs: [tools/supercontinent.py]
created: 2026-10-14
updated: 2026-10-23
---

## Description
Every L6 seed now reassembles above 25% of the surface at least twice in 2 Gyr (before, 3 of 4 never
did; showcase run 6d9dcf (deleted), seed 2). Shortfalls: uneven cycles (seed 1 quiet from 590 to 1930 Myr),
assemblies 400–870 Myr apart (Earth ~300–700). Option B from the decision: another round on regularity
(stronger continental insulation, shorter mantle memory). Pinned by the owner; revisit after PW-024.

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-15: From the supercontinent proposal (f45525c:docs/proposals/supercontinent_cycle.md). Acceptance criteria used: largest landmass >25% of the surface at least twice per 2 Gyr (L6, ~4 seeds); assemblies 300-700 Myr apart; 5-15 landmasses >0.5% between assemblies; land 25-35%, ocean age 50-90 Myr, speeds 2-8 cm/yr, runtime within ~10%. Fallbacks if more regularity is needed: (A) an imposed slowly rotating degree 1-2 mantle flow field with a period knob (cycles near-guaranteed, but metronomic and continents are told where to go; shares B's basal-drag term); (C, unbuilt part) interior oceans opened by a recent rift close preferentially - track each basin's parent rift, raise the margin-subduction hazard as it ages, optionally a weak attraction between plates sharing a recent suture (risk: accordion open/close of one ocean without whole-planet assembly). Rejected as the main route: C alone (cannot reach 25%), A (imposed). Owner accepted non-metronomic cycles and no guarantee for every seed. Side effect seen: land median 34-36% (up to ~40% assembled) and crust volume +2-5% mid-run while continents are assembled (fewer margins subduct).
- 2026-10-14: tectsea: with PW-024's warm_rift nudge, L6 seeds 1-4 x 2 Gyr assemble 4/3/3/2 times after the starting supercontinent (before 3/3/1/2), every 280-740 Myr (before 130-1360; seed 3 had none after 520).
- 2026-10-14: Owner (morning decision 5): looks better; pinned to come back to. Not urgent.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Crust and continents ('Supercontinent cycle') and morning decision 5.
