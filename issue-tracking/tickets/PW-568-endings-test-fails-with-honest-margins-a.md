---
id: PW-568
title: "Endings test fails with honest margins at L4 and at L5: the margin holds the ice, not the 440 km cells"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: ice-v2-stage1
blocked_by: []
relates: [PW-555, PW-460, PW-115]
refs: [tests/test_timezoom_cycle.py, planet/icemass.py, docs/review/ice-v2/stage-1.md]
created: 2026-10-22
updated: 2026-10-23
---

## Description
`test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast` (sim4, L4, 4 C colder, 6 C glacial by hand)
fails on the ice v2 lane. On the new main (after PW-549) the first ending keeps 62.5 of 60.7 m after 15 kyr (bar:
under half). The stage-1 handoff's "25 of 29 m" was measured on the old main.

Evidence (stage-1.md, "The L4 endings test"; scratch `icev2s1b/endtest.py` reproduces the test on any source and any
TZParams; L5 = the same recipe at level 5, seed 1, 300 Myr):

| rules | L4 left share | L5 left share |
|---|---|---|
| stage 1b defaults (ramp, seasons, cold, fetch) | 1.03 F | 0.83 F |
| stage 1 (surface_air=rest) | 0.98 F | 0.81 F |
| stage 1b, margin=edge | 0.36 ok | |
| main's zoom rules (edge, run k, all, all) | | 0.46 ok |

- It fails at L5 with the same bar, by nearly as much. Moving the test to L5 (option B) wouldn't make it pass.
- The ramp's two-point quadrature isn't the cause: against the exact mean over the ramp it is within 0.03-0.18 m/yr
  at L4 and 0.04-0.12 at L5 (`quadprobe.py`).
- So it is no resolution limit. The honest margin holds this planet's ice, and Earth's zoom shows the same at dT 0
  (draft-earth-zoom-does-not-hold-todays-ice-at-dt0).
Decision: keep the test at L4 unchanged (lean), and let it pass once the margin balance does (the dT-0 draft).
Don't loosen it or move it.

Stage 1c (front=ramp): extra 78.2 m, left 83.4 after 15 kyr: still fails, test unchanged. The honest front makes this
glacial bigger, not smaller, and the ending still holds it (draft-earth-zoom-does-not-hold-todays-ice-at-dt0).

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-l4-ending-test-with-honest-margins.md (found by ice-v2-stage1).
