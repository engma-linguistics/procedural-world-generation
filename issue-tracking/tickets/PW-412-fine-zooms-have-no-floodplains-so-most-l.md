---
id: PW-412
title: Fine zooms have no floodplains, so most lowland rivers count as confined and barely meander
type: task
status: done
parent: null
subsystem: zoom
effort: m
impact: med
found_by: pw405
blocked_by: []
relates: [PW-405, PW-404]
refs: [planet/zoom_fine.py, _courses, "zoom 352c76 (scratch regen, 170672 -> 3453b8 -> 25 m)"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-405 limits a meander train's swing by the valley floor's half width: where the parent's ground rises a couple of bankfull depths above the ground on the course. The fine landscape pass (stream-power profile from the imposed course) builds V valleys straight down to a 1-px channel. A floodplain never forms, even for a 300 m^3/s river at 0.04% slope. Such rivers come out "confined" and almost straight.

Example: 170672 -> 50 km @ 100 m (3453b8) -> 20 km @ 25 m. The 310 m^3/s river has a 0.04% bed and is alluvial and single-thread. Its parent floor is about 50 m wide, so it meanders only weakly: gentle sinuosity ~1.09 at q >= 10. On the open lowland of 3ac681 (980612 / b570c2), meanders do form.

Approach: along alluvial single-thread courses (the `_courses` classes), hold a flat floodplain at about bankfull level. Make it about the meander belt wide (2 x amplitude + w, at least ~10 w). The landscape pass then shapes hillslopes from the floodplain's edge. The planform's confinement test would then see the floor of a parent zoom made with this change.
- [ ] Watch the PW-389 3x3 block means: does the floodplain's missing volume go back onto the hills, or is it a drawn feature left out like gorges? Decide which.
- [ ] Lowland fine zooms show flat valley floors with meanders on them. Bedrock valleys stay V-shaped.

## Updates
- 2026-10-16: Status todo -> done. Done in 157ac20 (branch worktree-agent-ac1ccc6d516a5802f). planet/zoom_fine_floodplain.py: each alluvial reach (braided or single-thread) gets a valley floor round its axis, FLOOR_W 20 channel widths x sqrt(rock erodibility, evened over 2 parent px) x the reach's alluvial share (none on bedrock reaches). Its surface: half a bankfull depth (0.27 Q^0.39) above the course's water, levees 0.3 d over 2 widths, a rise of 0.5 d to the sides; its level is harmonic between the axes (no step at confluences). Beyond half a parent pixel it spreads only over the parent's low ground (max of the bicubic and the 3x3 block means, within a bankfull depth; gated spread, so it stays in one piece). It is held through the landscape pass and counted in the 3x3 means: the cut volume goes onto the hillslopes. Blocks mostly floor: 0.2-3 m rms (980612 1.7, b570c2 0.2, 2b1dab 3.0, 352c76 0.8). Overall block rms before -> after: 980612 0.72->0.94, b570c2 0.21->0.32, 2b1dab 1.16->1.31, 352c76 4.85->1.61; hilly zooms unchanged. A fine parent's floors are inherited (valley_floor / floor_m, bilinear); its own floors only where the parent drew none. Meanders: room = max(the parent's floor, this floor). 352c76 confined 93% -> 0% of drawn meanders; gentle sinuosity 1.09 -> 1.70 (p90 1.26 -> 1.87). Offsets now turn with the axis smoothed over a quarter wavelength: at full swing, the parent's pixel steps drew boxy loops. Switchbacks 0.027 -> 0.096/km (5 corners where loops meet valley bends; draft). Hilly 3e74b0: floors 0.1% of land, the gorge unchanged. New layers valley_floor (1 floor, 2 meander belt, 3 channel) and floor_m (the floor's surface, under the channel too), stats.floodplain: the hooks for PW-416. Decision on the checklist: the floor's volume goes back onto the hills (redistribution, not a drawn feature). Test test_valley_floors. Scratch verification: scratchpad/pw412 (metrics_before/after.txt, img/).
- 2026-10-16: Created from inbox draft draft-fine-zoom-floodplains.md (found by pw405).
