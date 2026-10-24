---
id: PW-681
title: "Health after A23 + A20 (merge lane 1024): pooled keyframes with ice sea level below -150 m go 3.8% -> 5.9% -> 7.45%, old ice bar fails 0 -> 2 of 16"
type: task
status: done
parent: PW-649
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: merge-1024
blocked_by: []
relates: [PW-592, PW-646, PW-611, PW-653]
refs: [docs/review/base-climate/merge-1024/, tools/health.py]
created: 2026-10-23
updated: 2026-10-23
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

## Updates
- 2026-10-23: Status todo -> done. Lane v1-finish verdict: the step-to-step moves were the draw (a pure basis re-draw moves single seeds 30-90 points), the level is signal: 32 L6 seeds quick, canonical basis, icehouse median 45% / mean 44 +- 5, owner's 40% bar passed by 50%, 5 always-icebox, 0 hellholes. Owned by PW-559 (balance = today's pCO2). Built PW-559 B (climate.PCO2_BALANCE 500 ppm): two draws 72% / 91% pass, icehouse median 19 / 14%, deep kf 11.0 -> 2.6%, no hellhole (max 27.6 C). On 1 Gyr (10 seeds) 5/10 pass: draft-late-history-cooling-1gyr. docs/review/base-climate/v1-finish/.
- 2026-10-23: Thermostat lane 1024 (in progress): seeds 201-216, A20 shelf air -> + PW-627: pooled deep share 11.0 +- 4.4 -> 9.8 +- 4.0%, icehouse +2.9 +- 10.1 points; no deepening on a fresh set, so the 101-108 jump at merge-1024 step 4 looks like those worlds' draw. 52f25a9, A22+A23 and PW-636 on 201-216 still to run. docs/review/base-climate/thermostat-1024/handoff.md.
- 2026-10-23: Created from inbox draft draft-health-drift-after-shelf-air.md (found by merge-1024).
