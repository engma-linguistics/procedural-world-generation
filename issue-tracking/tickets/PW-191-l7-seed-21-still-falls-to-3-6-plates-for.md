---
id: PW-191
title: L7 seed 21 still falls to 3-6 plates for 300+ Myr despite the warm-mantle rift nudge
type: task
status: in-progress
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: tectsea
blocked_by: []
relates: [PW-024, PW-025, PW-053]
refs: [planet/tectonics/events.py, tools/supercontinent.py, tools/sealevel.py, "run:cac9c4", "run:abcdac"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
PW-024's nudge (events.strength divided by 1 + warm_rift x the mantle anomaly,
warm_rift = 0.7) lifts plate counts at L6 (4 seeds x 2 Gyr: median 7 -> 9,
minimum 1 -> 3, share of samples with <= 4 plates 15.5% -> 3.2%), but the one
L7 check does not follow: run cac9c4 (L7, seed 21, 1 Gyr, tectsea code) has
15-21 plates for 0-350 Myr, then 3-7 plates from ~640 Myr to the end (3 at
800-848 Myr); before (abcdac) median 10, minimum 4, <= 4 plates 2% of frames;
after median 10, minimum 3, 11%. With few plates spreading slows, the ocean ages
and sea level sits low (the ocean-basin part near its -250 m limit, ~-230 m, for
640-1000 Myr; plus ~-150 m of ice at 848 Myr), so this also drives what is left
of PW-053's sea-level range at L7.
The nudge only acts on plates over warm mantle; a big plate over neutral or
cold mantle gets nothing. To try: look at the mantle under the big plates in
cac9c4's late spell (`tools/supercontinent.py` records mantle_under); count
sutures and absorptions against rifts there; check whether something in the
stress test scales with level (stress_min_plate, rift_min_piece and
settle_time are surface shares / times, but the cut sampling and the
coherence welds are per cell). One seed: run 2-3 more L7 seeds (or L6 seed 21 to
2 Gyr) before changing anything.
- [ ] L7 plate count over 2-3 seeds understood; a dip to <= 4 for > 100 Myr either explained or made rarer

## Updates
- 2026-10-15: Status todo -> in-progress. Foundation round, worktree tectfound.
- 2026-10-14: Created from inbox draft draft-l7-late-plate-collapse.md (found by tectsea).
