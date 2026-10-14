---
id: PW-121
title: Lake share on generated worlds fell to ~0.9-1.0% of land with the 0.1 m/km basin slope rule; keep it?
type: task
status: needs-decision
parent: null
subsystem: hydrology
effort: xs
impact: med
found_by: lakesize
blocked_by: []
relates: [PW-110, PW-058]
refs: [planet/hydrology.py, planet/kernels.py, "run c3bf56", "run 28e6be"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-110 (A + C) added `hydrology.MIN_SLOPE = 0.1` m/km: a closed basin must be
at least max(20 m, 0.1 m/km x sqrt(area / pi)) deep at its rim, or it drains.
It removes the giant flat lakes, but it also takes away about half the lake
area, because the generated L6 basins cluster right at this slope
(depth / radius ~0.07-0.14 m/km, so the rule is close to a switch for them).

Seed 13, L6, 600 Myr, same terrain (24 checkpoints of 4 runs), slope 0 -> 0.06 -> 0.08 -> 0.1:
- lake share of land 1.76 -> 1.40 -> 1.08 -> 0.90%; closed lakes 0.62 -> 0.41 -> 0.21 -> 0.11%
- land draining to closed basins 8.8 -> 6.9 -> 4.8 -> 4.2%
- lakes > 1M km^2: 13 -> 7 -> 3 -> 2; > 370k km^2 (Caspian): 43 -> 31 -> 19 -> 14
Fresh run c3bf56 vs 28e6be (all keyframes): lake share 1.63 -> 0.96%, frames with a
lake > 1M km^2 40% -> 13%, largest ever 3.6M -> 2.2M km^2. (Runs diverge
chaotically after the change, so per-run numbers are noisy; 0.06 and 0.08 runs gave 1.29% and 1.43%.)

Why 0.1: on Earth (L6 cell means) the artefact basins sit at 0.09-0.11 m/km
(Sudd 0.09, West Siberia 0.10, Amazon lowland 0.11) and real closed basins at
>= 0.2 (Caspian 2.4, Chad 0.4, Eyre 0.37, Tarim 1.6). With 0.08 the Sudd stays a
closed lake and the Nile vanishes again (0.10 of observed with GPCC rain).
And Earth's lakes that an L6 cell (~12,000 km^2) can show (lakes > ~6000 km^2)
cover only ~1.0M km^2, ~0.7% of land; the 1.5-2% figure includes many small lakes.

Options:
- A. Keep 0.1 (lean): consistent with Earth's basins; lake share ~0.9-1.0% is
  about Earth's share of resolvable lakes.
- B. Lower to 0.06-0.08: lake share 1.1-1.4%, but more 1M km^2 lakes and the
  Earth Sudd/Nile artefact returns.
- C. Keep 0.1 and compare lake share against Earth's resolvable lakes (~0.7-1%)
  in docs and the scorecard from now on.

## Updates
- 2026-10-14: Created from inbox draft draft-lake-share-after-slope-rule.md (found by lakesize).
