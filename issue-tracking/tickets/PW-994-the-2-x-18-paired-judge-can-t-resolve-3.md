---
id: PW-994
title: "The 2 x 18 paired judge can't resolve +-3 passes: a near-null change flipped 15 of 36 draws"
type: task
status: done
parent: null
milestone: v1
subsystem: climate
effort: s
impact: high
found_by: lane24
blocked_by: []
relates: [PW-980, PW-948, PW-438]
refs: [docs/review/base-climate/warm-drift/README.md]
created: 2026-10-29
updated: 2026-10-29
---

## Description
Lane 24 judged a change with almost no effect at L6: water conservation for the continents' sea (earth.continent_water,
+-20 m of sea level, land 34.80 -> 34.84%). It used the usual paired judge (L6 1 Gyr, 2 rolls x 18 draws, against
main b711afe6).
- Passes: 28/36 on main, 29/36 on the branch. 21 draws pass in both arms, 7 pass on main only, 8 on the branch only.
- Iceboxes: 10 against 13.
- Median end T: +0.85 against +1.63 C.
- The paired medians of the late dT differences were +1.0 C (roll 0.0005) and -0.7 C (roll 0.001).

So the chaos alone moves about 15 of 36 draws, shifts the pooled pass count by about +-3 and shifts the median end T
by about +-0.8 C. Lane 23's weld fix (31 -> 28, 6 to 3, +0.9 C) is inside that band. What lane 23 did show to be
systematic is the land share (+3.5 points) and the sink reference (+0.11 ln, about twice the null change's +-0.05).

Options:
- A. Keep 2 x 18 and read +-3 passes as "not worse" (PW-438's rule). Cheap, but a real 3-pass loss can't be seen.
- B. Use 4 rolls (72 draws) for climate changes, and for any change that lands within +-3. Cost: about 2x compute
  (about 5 h per arm at the current machine load).
- C. Keep 2 x 18 for the pass rate, and judge the mechanism on paired continuous measures with their spread from a
  null change: the sink and source references, late ln CO2, the land share. Lane 24's `decomp.py` already prints them.

Lean: C, plus B whenever the pass rate is the deciding fact (merging against a fitted kernel's loss).

## Updates
- 2026-10-29: Status todo -> done. Merged (lane 25): pjudge.py + paired.sh in docs/review/base-climate/v1-finish-16.
- 2026-10-29: Lane 25: built. docs/review/base-climate/v1-finish-16/pjudge.py (paired B-A medians with bootstrap 95% CI and sign test for end/moment T, late dT, late CO2, land, sink/source references, arid %, hot desert %, land rain, trees; pass count with both/A-only/B-only and McNemar p; SIM SUSPECT) and a generic paired.sh (any frozen code dir, any out root); README section on running and reading it, 4 rolls only when the pass count decides. First use: PW-015 round 1 (docs/review/base-climate/deserts/README.md).
- 2026-10-29: Status needs-decision -> todo. Coordinator 10-29 (owner defers methodology): judge merges on paired continuous measures (end T, late CO2, land, sink reference) with the pass count as a check; use 4 rolls only when the pass count decides a merge. Build this into the v1-finish harness in the next physics lane.
- 2026-10-29: Created from inbox draft draft-paired-judge-chaos-floor.md (found by lane24).
