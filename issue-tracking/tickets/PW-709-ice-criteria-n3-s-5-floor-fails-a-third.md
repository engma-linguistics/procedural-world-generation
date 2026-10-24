---
id: PW-709
title: Ice criteria N3's 5% floor fails a third of seeds on a 200 Myr quick window now that the balance is 500 ppm; the owner's v1 bar only caps the icehouse at ~40%
type: task
status: done
parent: null
milestone: v1
subsystem: climate
effort: xs
impact: low
found_by: v1-finish
blocked_by: []
relates: [PW-559, PW-681, PW-555]
refs: [tools/ice_criteria.py, docs/review/base-climate/v1-finish/, docs/review/ice-v2-criteria.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane v1-finish moved the carbon cycle's balance to 500 ppm (`climate.PCO2_BALANCE`, PW-559 B). On 32 L6 seeds with
`health --quick` (two draws), the icehouse share is now a median of 19% / 14% (Earth ~10-30%). 72% / 91% of seeds
pass the owner's v1 bar (at most ~40% icehouse). There's no hellhole: the hottest keyframe is 27.6 C.

The new ice bar (N1-N4, `tools/ice_criteria.py`) passes only 22 / 18 of 32, down from 23 on the old balance. Most
of the fails are now N3's floor, "icehouse 0% of the time, outside 5-70%". The quick sweep judges only 300-500 Myr,
and 200 Myr without an icehouse is ordinary for Earth (the Mesozoic). On the 1 Gyr ice_diag runs N3 has 700 Myr to
judge.

The thresholds are the owner's, so this lane left them unchanged. Options:
- A: keep N3 at 5-70%, and read the quick sweep's N3 fails as a short-window artefact (no change).
- B: make N3 the owner's bar (icehouse <= ~40%, floor 0) for v1, and keep 5% as a v2 variety goal.
- C: judge N3 only on runs of >= 1 Gyr (health's full sweep, ice_diag), and report it without judging on `--quick`.

Lean: C. The floor is about variety over a long history, and a 200 Myr window can't measure that. The cap is the
north-star check and stays judged everywhere.

## Updates
- 2026-10-23: Status todo -> done. Lane v1-finish-2 (5e552b9): tools/ice_criteria.py judges N3's 5% floor only on runs reaching FLOOR_RUN = 1000 Myr (res icehouse.floor_judged); the 70% cap and the rest on every window. No threshold moved; test in test_ice_diag; ice-v2-criteria.md's N3 row notes it.
- 2026-10-23: Status needs-decision -> todo. Coordinator's call: yes, judge N3's floor only on windows long enough to hold an ice age (>=1 Gyr runs); a window-scope change, no threshold moves.
- 2026-10-23: Created from inbox draft draft-n3-floor-against-owner-icebox-bar.md (found by v1-finish).
