---
id: PW-892
title: "World coastal layers (living reef, kelp) ignore the sea-life calendar: a `slice --ago 600` world still gets coral reefs"
type: task
status: done
parent: PW-244
milestone: v1
subsystem: coast
effort: s
impact: low
found_by: v1-finish-10
blocked_by: []
relates: [PW-807]
refs: [planet/coastal.py, planet/tectonics/earth.py, planet/timeline.py]
created: 2026-10-26
updated: 2026-10-28
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

## Updates
- 2026-10-28: Status todo -> done. Lane 21: run meta reef_builders_t, world meta vegetation.reef_builders (sim and keyframe paths), coastal.reef_builders gates the reef habitat and volcano reef rings (coral coasts follow). slice --ago 600 of run 479429: 0 reef cells (614 at the end). Kelp left as an inbox draft (no citable date in hand).
- 2026-10-26: Created from inbox draft draft-coastal-reefs-on-the-calendar.md (found by v1-finish-10).
