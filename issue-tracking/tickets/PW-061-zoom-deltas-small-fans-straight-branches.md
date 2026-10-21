---
id: PW-061
title: "Zoom deltas: small fans, straight branches, misplaced river mouths"
type: task
status: done
parent: null
milestone: null
subsystem: zoom
effort: m
impact: med
found_by: zoomwater
blocked_by: []
relates: []
refs: [planet/zoom.py, planet/coast.py, "zoom 00975d", "zoom f81832", "zoom ce4b72"]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Delta fans are small and their branches run straight (only 8 step directions). There are no
distributaries when the fine-scale river reaches the sea away from the coarse mouth, and the fine river
can reach the coast ~100 km from the coarse mouth, so the delta form and the river don't line up.
Demo zooms: 00975d (river), f81832 (wave), ce4b72 (tide).

## Updates
- 2026-10-16: Done: delta branches follow smooth wandering curves; bird's-foot fingers curve and taper; no branches to far coasts.
- 2026-10-16: Status in-progress -> done. Done: delta branches follow smooth wandering curves; bird's-foot fingers curve and taper; no branches to far coasts.
- 2026-10-16: Status todo -> in-progress. Zoom batch 5 agent started.
- 2026-10-15: PW-269 (merged d4e7c90): delta plains now 70 km x (Q/1000)^0.35 x (0.8+0.6 sf) (cap 350 km); biggest delta's plain 112 -> 349 km on an L7 world; 13/55 mouths tide-dominated (was 0). Re-check the fans in a zoom.
- 2026-10-14: Migrated. Merged: 'Delta fans are small' (zoomwater) and 'The fine river can reach the coast ~100 km from the coarse mouth' (deltas).
