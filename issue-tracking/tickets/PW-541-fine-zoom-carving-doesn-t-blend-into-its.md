---
id: PW-541
title: "Fine-zoom carving doesn't blend into its surroundings: box-shaped cuts with vertical walls around a sine-wave river (a7863f), deep pits round plunge pools"
type: task
status: todo
parent: PW-516
milestone: v2
subsystem: zoom
effort: l
impact: high
found_by: owner
blocked_by: []
relates: [PW-522, PW-532]
refs: [docs/review/screens/a7863f-box-walls.png, docs/review/screens/a7863f-stepped-falls-pools.png]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner 2026-10-21, fine zoom a7863f (25 km @ 50 m in 911ad8, world 28442c, 8.54 N -84.04 W). (1) A river runs as a regular sine wave with a 45 degree bend through flat-floored 'carved wetlands' bounded by sheer vertical walls hundreds of m tall: rectangular box cuts, insane in 3D, odd in 2D. (2) The stepped falls and their pools are acceptable (a bit circular), but they sit in deep pits whose sides don't fit the surrounding ground. Owner asks whether this is rivers not eroding their surroundings. Coordinator's hypothesis, to verify: the fine zoom carves features (floodplains/wetlands, gorges, pools) into the inherited ground by subtraction, with no hillslope response, so the cut leaves walls no real slope could hold; a threshold-slope or hillslope-diffusion pass after carving (slopes relax back toward a rock-dependent stable angle, filling toward the channel) would make the surroundings follow the river. Also check why the meander is a regular sinusoid and where the box shapes come from (pixel-aligned masks?). Note 911ad8 predates the PW-517 carve; a7863f was made with current code.

## Updates
- 2026-10-21: Created.
