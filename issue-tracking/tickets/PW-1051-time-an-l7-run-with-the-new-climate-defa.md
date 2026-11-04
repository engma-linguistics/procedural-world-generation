---
id: PW-1051
title: Time an L7 run with the new climate defaults against main under the same load
type: task
status: todo
parent: PW-247
milestone: later
subsystem: infra
effort: s
impact: low
found_by: lane27b
blocked_by: []
relates: [PW-247]
refs: [docs/review/speed/README.md]
created: 2026-10-29
updated: 2026-11-03
---

## Description
**In plain words.** The new climate settings make L7 runs faster, but how much faster was never measured fairly.
The old and new runs ran at different times, while other work was loading the machine by different amounts. The
new default's runs took 3279 s and main's took 11591 s (medians, 4 seeds, 1 Gyr), so 3.5x. The new runs had the
quieter machine, so that figure is too high. The estimate from per-update costs is ~2.9x.

Launch one L7 run of the merged default and one of main (287ca3d0) on the same seed at the same time, on a quiet
machine if possible, with the same NUMBA_NUM_THREADS. Record wall and CPU. Put the line in the Speed section of
docs/review/speed/README.md and in planet make's time estimates if they read from it. No judge draws are needed.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: tool or performance nicety
- 2026-10-29: Created from inbox draft draft-l7-speed-equal-load-timing.md (found by lane27b).
