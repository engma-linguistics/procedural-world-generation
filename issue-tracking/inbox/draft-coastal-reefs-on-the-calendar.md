---
title: "World coastal layers (living reef, kelp) ignore the sea-life calendar: a `slice --ago 600` world still gets coral reefs"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: coast
effort: s
impact: low
found_by: v1-finish-10
blocked_by: []
relates: [PW-807]
refs: [planet/coastal.py, planet/tectonics/earth.py, planet/timeline.py]
---

## Description
v1-finish-10 put the run's reefs on Earth's calendar counted back from the run's end (`earth.REEF_BUILDERS_MA`
545-520 Ma, per seed `earth.reef_builders_t`; before it microbial carbonate at `MICROBIAL_REEF` 0.1 of the rate).
The world-level coastal life (`coastal.environment`: the living `reef` layer, coral coasts, reef hazards) is gated
only by the plant groups (`unlocked`: seagrass and mangrove on flowering plants, salt marsh on grasses), not by
the reef builders. Default worlds are taken at the run's end, so they are right; a world asked for by age
(`slice --ago 600`) still gets living coral reefs.
- [ ] store the reef builders' arrival in run meta (beside plant_groups) and gate coastal.py's reef term on it
  (pre-arrival: stromatolite flats at most, no coral coast)
- [ ] kelp (brown algae, ~ Mesozoic-Cenozoic radiation) checked against the same calendar
