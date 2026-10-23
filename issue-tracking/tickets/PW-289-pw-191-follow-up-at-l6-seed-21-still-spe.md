---
id: PW-289
title: "PW-191 follow-up: at L6, seed 21 still spends 6% of its run at 3-4 plates (636-716 Myr), seed 11 2.5% (its cold era)"
type: task
status: todo
parent: PW-649
milestone: later
subsystem: tectonics
effort: m
impact: low
found_by: health-sweep
blocked_by: []
relates: [PW-191, PW-240]
refs: [docs/review/health/2026-10-15/report.md, tools/health.py]
created: 2026-10-15
updated: 2026-10-23
---

## Description
Follow-up to PW-191 (done). PW-246 health sweep (2026-10-15, main 6926583, 1 Gyr): at L7 the fix
holds (seeds 21/11/3199: plate minimum 7/8/5, medians 14/13/11, no keyframe at <= 4). At L6, seed 21
falls to 3-4 plates in 14 of 238 keyframes (5.9%) between 636 and 716 Myr (median 9.5, the lowest
of the 8 seeds), and seed 11 in 6 keyframes (2.5%) at 164-192 Myr, the supercontinent spell that is
also its deep cold era (CO2 index -1.1, -384 m of ice sea level; see the PW-240 update). The other 6
L6 seeds stay at >= 5. PW-191's L6 figure was 3.2% at <= 4 plates on 4 seeds x 2 Gyr, so this is the
known L6 tail rather than a regression; it matters mostly through the CO2/cold-era link. L6 runs
deleted; they reproduce from seed + 6926583.

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-15: Created from inbox draft draft-health-l6-seed21-few-plates.md (found by health-sweep).
