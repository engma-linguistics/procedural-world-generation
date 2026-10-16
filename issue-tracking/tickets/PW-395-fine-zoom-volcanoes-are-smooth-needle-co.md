---
id: PW-395
title: "Fine zoom volcanoes are smooth needle cones: no summit crater, gullies, flows or parasitic cones; ring at the held core's edge"
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-129, PW-394]
refs: [planet/zoom_fine.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner on fine zooms 6ea4c1 / bdff35 (stratovolcano, summit 3048 m, parent 193d10): "that's just a cone", with no crater or summit form; it looks silly. The cone is held smooth at the parent's surface with a needle tip, with a visible ring where the held core meets the noised terrain. The same applies to the arc-rock hills round lagoon a0097b: smooth 1 km blobs from the parent, with no fine detail (their 40-400 m heights are plausible, the shape isn't).

Wanted, from the parent's volcano table (kind, status, age, top_m), keeping top_m exactly as the crater rim's high point (owner rule: volcano summits exact):
- Summit form by kind and status: active/dormant stratovolcano has a summit crater (~0.3-1 km); a listed caldera has a caldera; a shield has a broad summit with a pit crater; extinct volcanoes are eroded, with a lower relief crater or none.
- Radial gullies (barrancos) deepening with age and rain, via the fine landscape pass instead of the held smooth core.
- Lava flow lobes and a few flank/parasitic cones on younger volcanoes.
- Upper flanks no steeper than ~30-35 degrees; no needle tip.
- No ring: blend the held core's edge into the noised surroundings.
Also apply the fine detail noise and hillslope pass to inherited smooth hills (arc rock, PW-394's case).

## Updates
- 2026-10-16: Created from inbox draft draft-fine-zoom-volcano-form.md (found by daniel).
- 2026-10-16: Implemented on branch worktree-agent-a17d3c46d5f25baf1 (zoom lane): new planet/zoom_fine_volcano.py draws each volcano's edifice below the parent's pixel scale (stratocone with a summit crater, rim notched, concave exponential flanks ~31 deg under the rim; extinct large stratocones a summit caldera; shields a steep-walled caldera and pit craters; radial gullies by status/age and rain, capped by their width; lava flow lobes and cinder cones on active/dormant ones). zoom_fine adds it to the parent's surface less its parent-pixel means (means kept). Where a coarse parent averaged the cone far below top_m (193d10's summit pixel is 2092 m for a 3048 m summit: the old needle), the cone stands on its floor as a drawn feature, left out of the 3x3 means like a gorge; stats gain parent_block_mean_rms_error_kept_m and drawn_cone_px. Summit form held with the rim's high point exactly top_m; flanks clamped to the edifice down to its lower flanks (the pass's stream-power steps stood as terraces on a 30 deg cone), then freed: no ring. Showcases (scratch regen, 6ea4c1 / bdff35): crater 0.6 km x 121 m, flanks 28 deg at 1 km falling to 12 deg at 4 km, slope p99 < 35 deg, kept-block rms 4.9 m (6ea4c1) / 2.4 m (bdff35). Not done here: the arc-rock smooth hills of a0097b (no volcano involved; draft filed); a volcano whose parent ground stands above its summit is left as the parent's (PW-394 case).
