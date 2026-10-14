---
id: PW-078
title: Hothouse 'wine country' has 41 °C summers
type: task
status: done
parent: null
subsystem: highlights
effort: xs
impact: low
found_by: hl2
blocked_by: []
relates: []
refs: [planet/highlights.py, "run 19385e"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The Mediterranean "wine country" highlight on the hothouse world picks a Köppen-correct Cs place with 41 °C
summers: correct, not appealing. Add a warm-month cap (e.g. ≤ 30 °C) to the score.

## Updates
- 2026-10-14: Status in-progress -> done. Added a warmest-month cap (MED_MAX_WARM_C = 30 C) to the Csa/Csb mask in highlights.mediterranean, documented in the module docstring. Hothouse world 4d7207 (old picks 47/43 C) now has no wine country; 28cfc4 drops its 32 C pick (now 29/29 C); 0f7abd and 7c5adf unchanged in kind (24-28 C). Cached highlight lists recompute on their own (VERSION is the file hash).
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Highlights.
