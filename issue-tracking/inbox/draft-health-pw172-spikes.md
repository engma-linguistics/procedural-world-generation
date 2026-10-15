---
title: "PW-172 update: one-frame 9.7-10.6 km single-cell spikes on 80 km crust in all 3 L7 seeds (health sweep)"
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: health-sweep
blocked_by: []
relates: [PW-172, PW-048, PW-285]
refs: [docs/review/health/2026-10-15/report.md, "run:550a5a@148Myr(5.73,162.02)", "run:550a5a@640Myr(-0.89,117.67)", "run:6114bd@944Myr(-41.03,-9.32)", "run:9068cb@512Myr(2.65,-124.10)"]
---

## Description
Update for PW-172. PW-246 health sweep (2026-10-15, main 6926583, 1 Gyr, keyframes every 4 Myr):
keyframes with a peak above 9.5 km: L7 seed 21 (run 550a5a) 4, seed 3199 (6114bd) 3, seed 11
(9068cb) 3; L6 seeds 21, 3199 and 2 one each (the other 5 L6 seeds none). Most are single cells
standing far above their neighbours for one keyframe, all continental with crust at 75-80 km:
| run | Myr | at | peak | neighbours (median) | frame before / after |
|---|---|---|---|---|---|
| 550a5a (L7 s21) | 148 | (5.73, 162.02) | 10534 | 2269 | 5864 / 2976 |
| 550a5a | 640 | (-0.89, 117.67) | 10350 | 995 | 5646 / 66 |
| 550a5a | 800 | (-43.47, 41.80) | 10142 | 911 | 1549 / 892 |
| 6114bd (L7 s3199) | 944 | (-41.03, -9.32) | 10616 | 2208 | -332 / 4133 |
| 9068cb (L7 s11) | 436 | (4.45, 115.21) | 9677 | 308 | -5579 / 198 |
| 9068cb | 512 | (2.65, -124.10) | 9815 | -87 | 22 / 111 |
| 9068cb | 640 | (63.16, -28.06) | 9947 | 692 | 6844 / 980 |
| ce9950 (L6 s2, deleted) | 668 | (8.92, -142.86) | 10186 | 589 | 1215 / 1403 |
The rest (6114bd 964/968, 550a5a 880, L6 s21 @792, L6 s3199 @180) are 9.6-9.7 km tops of 5-7 km
plateaus: plausible. 6114bd reproduces the coordinator's a1d3b9 exactly (944/964/968 Myr, 10.6 km).
The spikes jump from near sea level (or below) to ~10 km and back within 8 Myr, as PW-172 describes
(ISO_VOLCANO isostasy on thick sediment-filled cells); the crust at the 80 km mark in every case
suggests a thickness cap is involved too. L6 runs are deleted; seed 2 reproduces (deterministic).
- [ ] no single-cell one-frame peaks above 9.5 km in `tools/health.py` (peak_frames 0 at L7)
