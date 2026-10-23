---
id: PW-396
title: The cold-started rain kernel (RAIN_DAYS 20) is 2.5-10% off its steady state on generated planets' land, so worlds and the run's warm-started rain differ by that much
type: task
status: todo
parent: PW-649
milestone: later
subsystem: climate
effort: s
impact: low
found_by: pw387-warm-start
blocked_by: []
relates: [PW-387, PW-015]
refs: [planet/climate.py, docs/review/audit/pw387_warm_check.py]
created: 2026-10-16
updated: 2026-10-23
---

## Description
RAIN_DAYS' comment says 20 days of pseudo-time put Earth L6's regions within 1% of 60 days. On a
generated L6 run (seed 1, the first 60 Myr, every climate update) the cold 20-day kernel's annual land rain
is off a cold 60-day reference by L1 = sum|P - P_ref| / sum P_ref of 2.5-10% (mean 6.4%; ~10% in the first
30 Myr, ~2.5% later). The 99th-percentile cell is off by 5-55x: dry cells that should be near zero
but still have some rain. L7 is the same: 9.4% over the first 16 Myr.

PW-387's warm start (8 days from the last update's end state) lands closer to the 60-day reference than cold 20
days does: mean L1 2.7% at L6 and 1.9% at L7, with the p99 cell within 0.6-0.8x. So since PW-387 a run's
rain is better converged than the world made from it at the same moment (world creation and the Earth
checks start cold). The two differ by the cold kernel's error, mostly in dry interiors.

What to try: measure the convergence on Earth L6/L7 and two generated worlds, and set RAIN_DAYS (cold start only) so
land L1 is about 1%. A cold start costs 0.25 s at L6 and 2.2 s at L7 per 20 days, and worlds are made once.
Raising RAIN_DAYS changes worlds, earth_check and the goldens, so it belongs to the run-physics lane.
Measuring script: docs/review/audit/pw387_warm_check.py (`uv run python docs/review/audit/pw387_warm_check.py LEVEL MYR SEED WARM_DAYS`; it wraps climate._rain along a run and compares warm, cold 20 d and cold 60 d).
- [ ] cold-start land L1 against a 60-day reference <= ~1.5% on Earth and on two generated planets

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Created from inbox draft draft-cold-rain-kernel-not-converged.md (found by pw387-warm-start).
