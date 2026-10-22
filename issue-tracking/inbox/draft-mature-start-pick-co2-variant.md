---
title: "Mature start: pick the CO2 stock's variant ((a) reference set once vs (b) relief term), and the warm-up and run length"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: high
found_by: base-climate-laneB3
blocked_by: []
relates: [PW-576, PW-558, PW-559]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, tools/ice_criteria.py, tools/health.py, docs/review/base-climate/thermostat.md]
---

## Description
Branch worktree-agent-a6839a8fda5489c3d has the mature start and the CO2 stock, with the relief term behind
`params.co2_relief_myr` (200 = (b), 0 = (a); default 200). Full tables are in thermostat.md, Stage 3. 10 L6 seeds,
1 Gyr, judged after 300 Myr, main 5c4c0fd:

| | N1-N4 | share median (15-45%) | CO2 answer (in 0.35-0.9) |
|---|---|---|---|
| main | 3/10 | 70% (1) | +0.28 (3) |
| old start (a) | 4/10 | 66% (0) | +0.34 (3) |
| old start (b) | 9/10 | 40% (5) | +0.40 (5) |
| mature (a) | 8/10 | 43% (5) | +0.21 (3) |
| mature (b) | 6/10 | 41% (3) | +0.13 (1) |

- By the owner's rule, (a) is the one: on the mature start it passes the multi-seed bar without the relief term.
  Then remove the switch and the relief term (`ref_rate`'s second slot and `RELIEF`'s text in earth.py,
  `co2_relief_myr`, `test_relief_term_off`), and update the golden.
- Open point: (a)'s CO2 answer fell from +0.34 to +0.21 on the mature start
  (draft-mature-start-co2-answer-drop).
- Warm-up: 300 Myr is enough on the mature start (its surface transient is over by ~50-150 Myr). Judging after
  500 Myr changes no N1-N4 count and halves the sample. Default run length: 1 Gyr (`simulate --myr` defaults to 500,
  which leaves 200 judged Myr).
- [ ] owner picks (a) or (b)
- [ ] owner sets the warm-up (SPINUP in tools/ice_criteria.py and tools/health.py) and the `simulate --myr` default
