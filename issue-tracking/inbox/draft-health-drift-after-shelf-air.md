---
title: "Health after A23 + A20 (merge lane 1024): pooled keyframes with ice sea level below -150 m go 3.8% -> 5.9% -> 7.45%, old ice bar fails 0 -> 2 of 16"
type: task
status: todo
parent: PW-649
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: merge-1024
blocked_by: []
relates: [PW-592, PW-646, PW-611, PW-653]
refs: [docs/review/base-climate/merge-1024/, tools/health.py]
---

## Description
In merge lane 1024 (`docs/review/base-climate/merge-1024/README.md`), `tools/health.py --quick` on two seed sets
(defaults; 101-108), all in one session:

| tree | pooled % kf < -150 m (defaults / 101-108 / mean) | old ice bar F | new ice bar F |
|---|---|---|---|
| main 52f25a9 | 4.2 / 3.4 / 3.8 | 0 | 6 |
| + A22 + A23 (real pCO2) | 8.6 / 3.2 / 5.9 | 0 | 6 |
| + A20 shelf air | 7.6 / 7.3 / 7.45 | 2 (seed 11; seed 107 is icehouse 100% of the time) | 6 |

Every test is green on all of these, and the Earth bars hold. These are single chaotic 500 Myr runs: which seeds go
deep moves at every step. Still, the trend runs one way, deeper icehouses, as A23 predicted for real pCO2 (sink-side
changes move dT ~29% more). Before more sink-side physics lands, measure whether this is chaos or signal
(more seeds or re-rolled draws, as the multi-seed fixtures do). If it is signal, it belongs to the thermostat's gain
(PW-611 / PW-653), not to a fix on the shelf rule.
- [ ] health on a third seed set (e.g. 201-208) for main and the merged tree
- [ ] a verdict: chaos or signal, and which ticket owns it
