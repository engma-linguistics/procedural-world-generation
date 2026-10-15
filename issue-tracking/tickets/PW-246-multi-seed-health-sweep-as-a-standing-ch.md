---
id: PW-246
title: Multi-seed health sweep as a standing check (L6 x ~8 seeds, L7 x 3)
type: story
status: todo
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
- 2026-10-15: Created.
