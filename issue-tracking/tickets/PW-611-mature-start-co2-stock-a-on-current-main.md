---
id: PW-611
title: "Mature start + CO2 stock (a) on current main: the icehouse share splits the seeds (six at 51-69%, four at 11-38%); main's climate now holds ice ~0.5-1 C warmer"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: base-climate-laneB4
blocked_by: []
relates: [PW-559, PW-576, PW-555]
refs: [docs/review/base-climate/thermostat.md, planet/tectonics/earth.py, tools/ice_criteria.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
thermostat.md, Stage 4. 10 L6 seeds, 1 Gyr, judged after 300 Myr, on c1b2229 with PW-576 (a) landed:
- N1-N4 pass on 8/10 and the CO2 term runs against drift-made dT on 10/10. The CO2 answer is +0.32 C/C, with 5/10
  in band.
- **The icehouse share** is a median of 54%, with 2/10 seeds in 15-45% (the 5c4c0fd sweep had 43% and 5/10). Per
  seed: 1 56%, 2 69%, 5 14%, 7 51%, 11 38%, 13 60%, 21 11%, 42 23%, 99 62%, 3199 59%. N3's own band, 5-70%, passes on
  9/10.
- Pooled over the seeds, the share is unchanged: 44% of the steps against 46%. Main's climate changes since 5c4c0fd
  (PW-582, PW-579, stage 3) hold ice at a warmer dT. The share of steps in an icehouse goes 32 → 46% at dT +1..+2,
  19 → 30% at +2..+3, and 9 → 18% at +3..+4. The runs sit warmer (pooled median dT +1.1 → +1.8), and the seeds split
  into an icy group and a warm one.

Options:
- A: nothing. N3 passes, and 15-45% was the review's aim, not a criterion. Seeds differ, and a 0.5 C shift isn't a
  mechanism to fix.
- B: PW-559's set point. The stock's reference is the planet's own balance at 300 Myr, so a small warm offset in it
  (option B there) moves every seed's mean. Measure it on the 10 seeds.
- C: before touching the carbon cycle, find out why the cold side holds ice 0.5-1 C warmer since stage 3 (lane A's
  ice and ocean work).

Lean: C first, as a measurement: the ice-vs-dT curve on main against 5c4c0fd at a fixed moment. Then B, but only if
the cause is a sound mechanism and the share still sits high.
- [ ] owner picks A, B or C

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Created from inbox draft draft-icehouse-share-split-on-main.md (found by base-climate-laneB4).
