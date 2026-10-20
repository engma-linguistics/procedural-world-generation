---
id: PW-177
title: "Dune fields: seams between drift patches, network dunes, unresolved barchans"
type: task
status: todo
parent: PW-096
subsystem: zoom
effort: m
impact: low
found_by: zoomland3
blocked_by: []
relates: [PW-012]
refs: [planet/zoom_landforms.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
PW-012's Dunes synthesiser draws the big dunes (draas) at least 5 px
apart on planet-fixed ~200 km patches oriented by the sand drift. Left:
- where two patches meet the crests switch over a narrow wandering seam;
  where transverse and linear weights mix (RDP/DP ~0.75) the two patterns
  cross-hatch (zoom 2d1537 (deleted), upper right): real mixed regimes make network
  or crescentic-linear dunes, which could be drawn instead;
- barchans are 0.1-0.5 km: a 0.5 km zoom shows only exaggerated crescents
  (ee587f: low and faint); a nested fine zoom (PW-129) would be the place;
- star dunes are radial-armed peaks on a lattice, all alike; their arms
  could follow the wind modes;
- dunes don't interact with the rivers that cross the erg (no blocked
  wadis or interdune lakes) nor climb the hills' windward sides.

## Updates
- 2026-10-16: Status in-progress -> todo. Coordinator 2026-10-16: seams confirmed; parked (phasor noise is the option if dunes get attention later).
- 2026-10-16: Stopped (zoom batch 6): looked at, not changed; the seams' fix is a design choice. On 592f2a the big erg is ~2,000 cells round 31.9,30.5 (BWk; 250 km @ 0.5 km at 32.3,31.2, seed 1: transverse/barchan 0.92, linear 0.08, spacing 1.9 km, crests up to 134 m; image docs/review/zoom-polish/pw177_seam.png). The seam is as described: two planet-fixed ~200 km patches each with its own axis and phase, switched over a narrow wandering band (smoothstep 0.42-0.58 of the frames' blend + noise), so crests end against a line where the orientation jumps ~30-60 deg; widening the blend brings back the cross-hatch, and blending the patches' coordinates instead (bent crests) distorts the spacing by the patches' offset (hundreds of km x the blend's gradient). Options: A) phasor noise (Tricard et al. 2019: a sum of oriented Gabor kernels whose phase, not just amplitude, is kept), the kernels' orientation taken from the local drift per pixel: a continuous orientation field with no patches, the existing transverse/linear profiles applied to its phase; also gives network dunes where two drift modes mix (two kernels' orientations) and lets star dunes' arms follow the wind modes; a new numba kernel, m-l. B) keep the patches, draw the mixed regime as crescentic-linear (linear ridges modulated by the transverse crests, z = zl x (a + b zt)) instead of the weighted sum, and orient star arms by the patch's axis: s, leaves the seams. C) accept (seams are faint at 1-4 km, visible at 0.5 km). Barchans (0.1-0.5 km) stay for a nested zoom (PW-129); dunes vs rivers/hills unchanged. Lean: A if the owner wants ergs to read right at 0.5 km, else C; B is a partial.
- 2026-10-16: Status todo -> in-progress. Zoom batch 6 agent started.
- 2026-10-14: Created from inbox draft draft-dune-detail.md (found by zoomland3).
