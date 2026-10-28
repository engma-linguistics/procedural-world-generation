---
title: Kelp forests aren't on the sea-life calendar (a `slice --ago 600` world still gets kelp)
type: task
status: todo
parent: PW-244
milestone: null
subsystem: coast
effort: s
impact: low
found_by: physics-lane-21
blocked_by: []
relates: [PW-892]
refs: [planet/coastal.py, planet/tectonics/earth.py, planet/timeline.py]
---

## Description
Lane 21 (PW-892) put the world's living reefs on the run's calendar. The run meta now stores `reef_builders_t`,
the world meta stores `vegetation.reef_builders`, and `coastal.reef_builders(meta)` gates the reef habitat and
the volcano reef rings. Kelp is still gated by nothing. True kelps (Laminariales) are a young group; they appear
in the Cenozoic, long after the reef builders. Lane 21 did not take an arrival date for them, because it had no
source it could cite with confidence.

What to try: find a dated source for the kelps' origin (a fossil-calibrated phylogeny of the Laminariales, or the
oldest kelp-forest fossils). Store a `kelp_t` beside `reef_builders_t` on the same counted-back calendar (a
per-seed draw over the dated window), and gate `coastal.environment`'s kelp term with it. Before kelp, rocky cool
shores would have other brown and red algal turf, not forests.
- [ ] a cited arrival window
- [ ] kelp gated like the reefs, with a test like `test_no_living_reef_before_the_reef_builders`
