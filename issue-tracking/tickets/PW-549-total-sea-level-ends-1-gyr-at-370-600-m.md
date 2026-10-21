---
id: PW-549
title: Total sea level ends 1 Gyr at -370..-600 m in 7 of 8 runs of the v1 batch (26-48% of keyframes outside -250..+300 m)
type: task
status: todo
parent: null
milestone: v1
subsystem: ocean
effort: m
impact: high
found_by: pw548
blocked_by: []
relates: [PW-434, PW-051, PW-293, PW-300, PW-430]
refs: [docs/review/health/2026-10-21-batch/report.md, tools/health.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Health check of the existing v1 batch runs (runs 9b685e 0ecb0d 865ea0 3ff3f3 1112ef 6a0029 396621 f9e085, 1 Gyr, 251 keyframes; no new simulation). Total sea level (ice plus ocean-basin term, `sea_level`) has medians of -65..-240 m but minima of -520..-1055 m (run 396621 -1055 m), and the last keyframe is -374..-597 m in 7 of 8 runs (only 9b685e ends at +47 m). 26-48% of each run's keyframes are outside the -250..+300 m envelope. The ice part alone (`sea_ice_m`) is outside -250 m in 0-15% of frames (396621: 26%), against 26-48% for the total, so a large part of the depth comes from the basin term (PW-051, PW-293), not just from PW-434's thicker ice sheets. Worth checking whether PW-434 alone brings it in, or whether the ocean-basin reference drifts as plates and ocean age change over a Gyr.
- [ ] split `sea_level` into ice and basin terms per keyframe for these runs and find which one drives the -400 m ends
- [ ] decide whether the envelope (-250 m) or the model is wrong; Phanerozoic range is -130..+250 m

## Updates
- 2026-10-21: Owner 2026-10-21: leave the first ~100 Myr (warm-up) out of the sea-level band.
- 2026-10-21: Measured with PW-514 option A (docs/review/audit/PW-514-option-a.md, 10 L6 1 Gyr seeds): the deep ends are mostly the ocean-basin term, which tracks the floor's mean age (corr -0.87..-0.97 on every seed). The floor ages from ~50 Myr (the 48 Myr reference) to 61-130 Myr by 1 Gyr. coast_loss makes the ice part milder (median end -27 m against -100) and doesn't touch the basin term. Main end median -328 m (4/10 below -370), branch -113 m (3/10).
- 2026-10-21: Created from inbox draft draft-batch-sea-level-ends-deep.md (found by pw548).
