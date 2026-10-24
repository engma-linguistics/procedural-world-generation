---
id: PW-707
title: Best-of-N wish scores swing 0.05-0.1 between picks; judge wish-dynamics changes on the mean of the tries
type: task
status: todo
parent: null
milestone: v2
subsystem: infra
effort: xs
impact: low
found_by: fun-lane-3
blocked_by: []
relates: [PW-635, PW-699]
refs: [planet/lineages/history.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
With the same seeds (tree seed 7: tries 7000-7003) the per-try wish scores on 1df1c3 are 0.611 / 0.802 / 0.746 / 0.731 and on 3e9e7d 0.776 / 0.758 / 0.811 / 0.697, so the stored best of N moves by up to 0.1 between configurations that differ only by chance, and the empty land of the kept try (2.9% to 18.9% on the same worlds) follows the pick. A run is deterministic for a given code and seed, so the per-try list in `meta.present.tries` is the paired comparison to use.

Suggestion: store the empty land and the composition numbers per try next to `tries` (cheap: they come out of the same present frame), and compare changes by the mean over >= 4 tries, with the best-of-N pick reported separately. `simulate` already keeps `tries`; add `try_stats`.

## Updates
- 2026-10-23: Yes: store per-try stats; judge wish-dynamics changes on the mean of >=4 tries.
- 2026-10-23: Created from inbox draft draft-wish-score-needs-mean-of-tries.md (found by fun-lane-3).
