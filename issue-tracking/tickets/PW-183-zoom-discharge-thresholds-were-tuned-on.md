---
id: PW-183
title: Zoom discharge thresholds were tuned on rain-routed discharge; review them now that streams carry runoff
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoompolish
blocked_by: []
relates: [PW-180, PW-125]
refs: [planet/zoom.py, planet/zoom_landforms.py, "zoom:2d06f8", "zoom:130acd"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
PW-180 made zoom streams carry the world's runoff instead of its rain. On
an Earth-like world land runoff is ~27% of the rain, so local streams now
carry ~1/4 (savanna, 2d06f8: ~1/5; wet f9b027: ~1/2) of what they did.
Two thresholds were moved with it: WF_MIN_Q 50 -> 20 m3/s (listed falls)
and GORGE_Q 100 -> 30 m3/s (a landform scarp's fall retreating into a
gorge). Falls after the change: f9b027 42 -> 40, 83e518 27 -> 30, but the
semi-arid escarpment demo 2d06f8 15 -> 6 and 130acd 21 -> 9 (its 'drop'
falls on 60-150 m3/s streams now carry 15-40). That is the honest result
of a dry climate, but the others still sit on the old scale and may need
the same look: SINK_Q 30 (karst streams sinking), Dunes.overlay_q 30
(wadis ending in the sand), BASIN_THROUGH_Q 100, GAP_Q, BANK_MAX_Q.
Check a karst demo and a rift basin zoom for fewer through-flowing rivers
than intended, and decide per threshold whether it is physical (keep) or
a visual tuning (scale by ~1/3).

## Updates
- 2026-10-15: Status todo -> done. Reviewed (vegzoom): thresholds already in mean discharge since PW-180; no change needed.
- 2026-10-14: Created from inbox draft draft-zoom-q-thresholds-runoff.md (found by zoompolish).
