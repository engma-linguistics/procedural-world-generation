---
id: PW-246
title: Multi-seed health sweep as a standing check (L6 x ~8 seeds, L7 x 3)
type: story
status: done
parent: PW-244
subsystem: infra
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-10-15
updated: 2026-10-15
---

## Description
The scorecard runs 2 seeds; several problems only showed on particular seeds (plate collapse seed 21, cold eras seeds 2/11). Build tools/health.py: run ~8 seeds at L6 and 3 at L7 (1 Gyr), and for each check Earth-ish envelopes over time (land share, crust thickness and area, plate count, ocean age, sea level from ice, dT range, inland drainage, lake share, giant lakes, peak heights, tree cover, NPP, determinism), plus a few rendered thumbnails per seed. Report outliers per seed and time. Run after every model-changing merge batch; record results in docs/review/health/. First run doubles as the post-merge integration check.

## Updates
- 2026-10-15: Second full sweep after the audit fixes: docs/review/after-audit-2026-10-15/health (42 min, 11 workers x 3 threads; 327 outlier spells vs 479; determinism bit-identical).
- 2026-10-15: Status in-progress -> done. Done: tools/health.py (merged 81f2445); first sweep docs/review/health/2026-10-15/ (50.7 min, 11 workers x 2 threads; determinism bit-identical; L7 seed 3199 reproduces a1d3b9). Kept L7 runs 550a5a (seed 21), 9068cb (seed 11).
- 2026-10-15: Status todo -> in-progress. Agent started: tools/health.py and the first sweep on the Threadripper.
- 2026-10-15: Created.
