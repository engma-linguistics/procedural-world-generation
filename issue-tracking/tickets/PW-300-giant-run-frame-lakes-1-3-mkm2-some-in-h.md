---
id: PW-300
title: Giant run-frame lakes (1-3 Mkm2, some in hyperarid basins) are on the frames' own terrain, not a stale-lakes artifact
type: task
status: blocked
parent: null
subsystem: hydrology
effort: m
impact: med
found_by: surface-hydro
blocked_by: [PW-358]
relates: [PW-239, PW-054, PW-284]
refs: [planet/hydrology.py, planet/tectonics/output.py, "run 9366df", "run ef2c6a", docs/review/audit/fixes-surface-hydro.md, docs/review/audit/pw293-sea-level.md, docs/review/health-pw293-before/, docs/review/health-pw293-after/]
created: 2026-10-15
updated: 2026-10-16
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
- 2026-10-16: Status in-progress -> blocked. Diagnosed (basins lane, docs/review/audit/basins-lakes.md): lake water balance sound (inflow = evaporation within ~3%); giant lakes are closed lakes on broad flat hollows 30-150 m below their rims, just short of spilling; with open-water evaporation -15%, 5 of 8 spill and drain. Open-water evaporation is Oudin on TOA radiation x1.2 with no clouds/humidity: 1800-2030 mm/yr in humid climates vs ~1300-1600 observed (PW-358). Hollows mostly made by plate motion/resampling each step (PW-359). Seed noise on giant-lake frames ~+-2.5 points.
- 2026-10-16: Basins-lakes lane diagnosis (8 L6 seeds, health frames replayed): (1) the lake water balance is sound: on 8 giant frames basin inflow = evaporation off the lake within a few %, open lakes fill their hollows; (2) the hollows are broad flat-floored continental plains 30-150 m below their rims on ~37 km crust, no plate boundary; per-substage budget: resolve (plate motion + resampling) makes most hollow volume each step, plume-swell decay, arcs/plumes and the moat recompute the rest, erosion fills them within a few Myr (giant lakes flicker); (3) giant closed lakes sit just short of spilling: lake_evap x 0.85 turns 5 of 8 open and they drain to their outlet valleys (6.85 -> 0.11 Mkm2 etc.). Humid-climate open-water evaporation (Oudin on top-of-atmosphere radiation x 1.2: 1800-2030 mm at 23-27 C) is the likely cause of closed lakes under 1000-1700 mm of rain: climate.py, outside this lane (draft). No sound in-scope fix found; flexure off (diagnostic) 8.8 -> 6.1%, no floodplains 9.8%, no hotspots 10.3%, a mean-depth MIN_SLOPE rule 10.8% (seed noise ~+-2.5 points). Details: docs/review/audit/basins-lakes.md.
- 2026-10-16: Status todo -> in-progress. Run-lane agent started (basins and giant lakes).
- 2026-10-15: Merged inbox draft draft-giant-lakes-lower-sea.md ("Giant run-frame lakes doubled when sea level came down ~130 m (PW-293); evidence for PW-300", found by pw293).
  Evidence for PW-300 (coordinator: probably `--merge-into PW-300`). PW-293 moved the run's median sea level
  from +148 to +15 m (health --quick, 8 L6 seeds x 500 Myr, same seeds). Keyframes whose biggest lake is over
  1 Mkm2 rose from a mean of 5.2% per run to 9.6% (per seed before -> after: 1: 2.7 -> 10.6, 2: 3.5 -> 1.8,
  11: 4.4 -> 14.2, 21: 10.6 -> 18.6, 3199: 2.7 -> 11.5, 42: 2.7 -> 1.8, 77: 13.3 -> 10.6, 505: 1.8 -> 8.0), and
  lake_max spells outside the envelope 34 -> 40. The lake share of land is unchanged (median 0.5%) and the land
  share is unchanged (33.4 -> 33.5%), so this isn't more land. Likely mechanism: a sea ~130 m lower leaves
  low continental interiors that a +150 m sea used to flood as epicontinental seas above the sea, as closed
  basins that fill into giant lakes. If so, PW-300's giant lakes depend on how deep the low interiors are (the
  erosion base level, sag, PW-054's closed basins), not on sea level, and a fix there should be checked at
  today's sea level. Not checked cell by cell; the 8 seeds diverge chaotically, so part of it may be chance.
- 2026-10-15: Post-audit sweep: giant lakes are now the top outliers (seed 11 L7 22% of frames with a >1 Mkm2 lake; L6 lake_max up to 6.6 Mkm2).
- 2026-10-15: Created from inbox draft draft-giant-lakes-on-final-terrain.md (found by surface-hydro).
