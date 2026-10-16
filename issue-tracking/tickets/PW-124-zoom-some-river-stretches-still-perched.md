---
id: PW-124
title: "Zoom: some river stretches still perched (under ice, beside other rivers)"
type: task
status: wontdo
parent: null
subsystem: zoom
effort: m
impact: low
found_by: zoomsmalls
blocked_by: []
relates: [PW-068]
refs: [planet/zoom.py, "zoom:1ef6c5", "zoom:3ea62e", "world:f724bd(54.0,-23.14)"]
created: 2026-10-14
updated: 2026-10-16
---

## Description
PW-068 gave reaches with falls valley sides a few km wide (`banks()`): over 20 test zooms the river
pixels (>= 100 m3/s) with land within 2 px more than 30 m below them fell 702 -> 195 (> 100 m:
260 -> 11, worst 869 -> 364 m). What is left:
- under ice, where creep may lift a stream's bed (ICE_SNOUT_GRAD) and the land beside drains lower;
- where the banks skip another river (>= BANK_MAX_Q or another coarse river's valley bottom), so a
  lower parallel river runs within 2 px;
- the banks lift the land to the river rather than lowering the river: where a staircase sits far
  above the fine land, the result is a raised strip ~8 km wide with 30 m/km flanks. Fitting the
  staircase under the fine surface (e.g. the previous iteration's land around the course) instead
  of the coarse ground would lower the river with the land.
Metric: for river pixels >= 100 m3/s, min over land (< 30 m3/s) within 2 px vs the min river level
within 2 px of that land pixel.

## Updates
- 2026-10-16: Status in-progress -> wontdo. Coordinator 2026-10-16: accept for now (option B fixed one case but raised drops to 10.6-10.8 per seed). Remaining perched pixels 38.6/seed after PW-363.
- 2026-10-16: Stopped (zoom batch 6): option B tried, not merged (a trade-off against the drops). Tried: from a third of the way through the landscape pass, unpin a falls reach's course pixel where active land off the course within the banks' width (BANK_KM, >= 2 px) lies > T below it on the iteration's surface; place_falls then follows the river. Held pinned within banks+3 px of each lip and its gorge (else the river left the plateau 2-5 px above the lip: arc seed 3's 693 m lip became a 684 m 'drop'). 592f2a's 8 zooms + plateau, seeds 1-5 (base: drops >= 100 m 9.8 per seed, perched 56.2, > 100 m 5.0): T = 30 m: drops 10.8, perched 50.8, > 100 m 3.8; T = 100 m: drops ~10.6, perched 53.4, > 100 m 2.8; lips' total height unchanged; inland bias/RMS unchanged. Case 2 is fixed outright (-2.22,-169.11 seed 4: 16 -> 0 px; the river takes the deeper fine valley and the reach settles ~100 m lower), but where the lower land is a plain or valley beside a staircase (arc -9.35,-161.39 seeds 2/3/5 at ~(314,116); 49.32,37.38 seed 2 at (131,481)) the freed river leaves the stair down a new undesigned 100-130 m drop, and the arc's own perched px hardly move (47 -> 45-48: they are case 1, side tributaries graded to the foot, and PW-363's raised distributaries, 37 of seed 2's 63). Options: (a) take B at T = 100 m (+0.8 drops per seed for -2.2 perched > 100 m px); (b) B only where the lower valley drains back to the same reach below (needs a drainage test per freed pixel); (c) accept: case 1 is the banks' design at 4 km/px, case 2 one seed of one zoom. Lean: c now, revisit after PW-363 (the arc's metric is mostly its distributaries). Patch kept out of the branch.
- 2026-10-16: Status todo -> in-progress. Zoom batch 6 agent started.
- 2026-10-16: Stopped (zoom batch 5): 41 perched pixels per seed, all on designed-fall reaches; agent lean: let the pinned course move to the fine valley bottom. Coordinator: take the lean in the next zoom batch.
- 2026-10-16: Status in-progress -> todo. Stopped (zoom batch 5): 41 perched pixels per seed, all on designed-fall reaches; agent lean: let the pinned course move to the fine valley bottom. Coordinator: take the lean in the next zoom batch.
- 2026-10-16: Zoom batch 5: measured, not changed (a design trade-off). Metric (river px >= 100 m3/s with land < 30 m3/s within 2 px lying > 30 m below every river px within 2 px of it) on the 8 showcase zooms of 592f2a, seeds 1-5: 41 px per seed-set (of ~15k river px), 4.8 > 100 m, worst 70-490 m; 30 of the 41 on the arc zoom -9.35,-161.39. Under ice: 0.4 (was the ticket's first case; gone). Beside other rivers: none found. Every remaining case is on a pinned designed-fall reach (plus ~5 delta distributaries on the arc, levee-bound by design): (1) at 4 km/px the banks are 2 px flat then fall at BANK_SIDE_GRAD 30 m/km, so land 2 diagonal px (11 km) off may sit 99 m below the river: the arc's ~30 px, 30-120 m (side tributaries graded to the river below the reach's falls); (2) the course pinned to the coarse polyline runs along a valley side above a deeper fine valley (-2.22,-169.11 seed 4: 16 px, 115-160 m, east side 640-750 m vs river ~890 m); (3) a lip's gorge beside the upper reach (49.32,37.38 seed 3: 1704 m tread, gorge 1266-1308 m within 2 px). Options: A) lower each reach's staircase to the land beside it (per-reach offset, tapered at the head so the river above doesn't gain an undesigned drop); B) let the pinned course move to the fine valley bottom where it lies lower within the banks' width (unpin there), the staircase following the river as place_falls already does; C) accept: case 3 is natural (Niagara's gorge beside its upper river) and case 1 is within the banks' design at 4 km/px. Lean: C for 3, B for 2, and B would also take most of 1. Scripts: perched metric in docs/review/zoom-polish/batch5.md.
- 2026-10-16: Status todo -> in-progress. Zoom batch 5 agent started.
- 2026-10-14: Created from inbox draft draft-zoom-perched-rivers-left.md (found by zoomsmalls).
