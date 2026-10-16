---
id: PW-300
title: Giant run-frame lakes (1-3 Mkm2, some in hyperarid basins) are on the frames' own terrain, not a stale-lakes artifact
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: med
found_by: surface-hydro
blocked_by: []
relates: [PW-239, PW-054, PW-284]
refs: [planet/hydrology.py, planet/tectonics/output.py, "run 9366df", "run ef2c6a", docs/review/audit/fixes-surface-hydro.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The health sweep blamed PW-239 (frames storing the pre-step lakes) for giant 2-7 Mkm2 salt lakes. With PW-239
fixed (frames route on their final terrain) they remain: share of frames (100-500 Myr) whose biggest lake is
over 1 Mkm2: L6 8 seeds 17.2% (main) -> 11.3% (PW-280/282) -> 13.4% (with PW-239); L7 seeds 3199/21 4.0% ->
10.4% -> 12.9% (L6 and L7 now agree; L7 rose because its hillslopes wear half as hard since PW-282). Largest
5.0 Mkm2 (L6), 3.2 (L7).
Examples (L7 seed 3199, run 9366df): t 412, a 3.2 Mkm2 closed lake at ~900 m, median rain on it 129 mm;
t 488, 2.0 Mkm2 closed, 9 mm of rain; t 496, a 3.1 Mkm2 open lake 1.4 km deep (median) at ~1 km on 16 mm
of rain. Seed 21 (ef2c6a) has 1-1.4 Mkm2 closed lakes under 1000-1700 mm of rain (a closed lake should be
small where it is that wet). Worth checking: whether these hollows come from the flexural moat and sag
(PW-284) deepening interiors faster than they fill; whether the lake water balance uses catchment inflow that
the frame's terrain actually delivers (closed lakes under heavy rain), and whether a 1.4 km-deep 3 Mkm2 hollow
appearing in one frame is a tectonics step artifact. Runs 9366df / ef2c6a are in the surface-hydro worktree
(deleted before merge; rerun `tools/health.py --l6 --l7 3199 21 --myr 500` to get them back).

## Updates
- 2026-10-15: Created from inbox draft draft-giant-lakes-on-final-terrain.md (found by surface-hydro).
