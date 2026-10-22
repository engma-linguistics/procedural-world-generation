---
id: PW-549
title: Total sea level ends 1 Gyr at -370..-600 m in 7 of 8 runs of the v1 batch (26-48% of keyframes outside -250..+300 m)
type: task
status: done
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
updated: 2026-10-22
---

## Description
Health check of the existing v1 batch runs (runs 9b685e 0ecb0d 865ea0 3ff3f3 1112ef 6a0029 396621 f9e085, 1 Gyr, 251 keyframes; no new simulation). Total sea level (ice plus ocean-basin term, `sea_level`) has medians of -65..-240 m but minima of -520..-1055 m (run 396621 -1055 m), and the last keyframe is -374..-597 m in 7 of 8 runs (only 9b685e ends at +47 m). 26-48% of each run's keyframes are outside the -250..+300 m envelope. The ice part alone (`sea_ice_m`) is outside -250 m in 0-15% of frames (396621: 26%), against 26-48% for the total, so a large part of the depth comes from the basin term (PW-051, PW-293), not just from PW-434's thicker ice sheets. Worth checking whether PW-434 alone brings it in, or whether the ocean-basin reference drifts as plates and ocean age change over a Gyr.
- [ ] split `sea_level` into ice and basin terms per keyframe for these runs and find which one drives the -400 m ends
- [ ] decide whether the envelope (-250 m) or the model is wrong; Phanerozoic range is -130..+250 m

## Updates
- 2026-10-22: Status todo -> done. Fixed (pw549): the deep ends are the basin term, and its reference was measured on the wrong window. PW-293 set sea level 0 from the first 500 Myr, mostly the starting supercontinent's breakup (stress rifts 10-16 per 200 Myr, floor ~48 Myr); after the 300 Myr warm-up the model's ocean averages -4962 m / 62 Myr (10 L6 seeds), so later frames read ~-75 m low and old-floor seeds -150..-350. OCEAN_MAX_AGE 144 -> 162 (start mean 54 Myr; depth_ref -4968..-4977). After 300 Myr, total sea level within -250..+300 m: median 72% -> 92% of keyframes, seeds >= 80%: 3/10 -> 7/10; min median -543 -> -371. Cold-era check 8/10 -> 7/10. Warm-up now reads a breakup highstand (L4 +43..+83 m). Tried and reverted: a mantle heat budget (Tozer), too weak because slab-driven plates run at terminal speed. Rift die-out after ~600 Myr left as inbox draft. Write-up docs/review/audit/pw549-sea-level.md.
- 2026-10-21: Measured with PW-514 option A (docs/review/audit/PW-514-option-a.md, 10 L6 1 Gyr seeds): the deep ends are mostly the ocean-basin term, which tracks the floor's mean age (corr -0.87..-0.97 on every seed). The floor ages from ~50 Myr (the 48 Myr reference) to 61-130 Myr by 1 Gyr. coast_loss makes the ice part milder (median end -27 m against -100) and doesn't touch the basin term. Main end median -328 m (4/10 below -370), branch -113 m (3/10).
- 2026-10-21: Created from inbox draft draft-batch-sea-level-ends-deep.md (found by pw548).
