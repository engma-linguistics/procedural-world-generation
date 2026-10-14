---
id: PW-127
title: "Zoom glaciers ignore the fine temperature: ice drawn on warm valley floors"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-102]
refs: ["zoom:81f0f6", planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner spotted hot desert (BWh, ~1250-1600 m) at zoom 81f0f6 (1.49,-41.47) hemmed in by ice on three sides, and the ice pixels report well-above-0 C means. In 81f0f6: 41% of ice pixels have mean T > 0 C, 30% > 5 C, 10% > 16.8 C, and 10% of the ice lies below 427 m. Two causes: (1) the source world f724bd predates the PW-102 ice fix (old world-frame ice); (2) zoom.py draws glaciers from the interpolated coarse ice plus noise and a height bonus (glacier = ice > 1 & ice_eff > 40) without checking the fine pixel's own climate, so a coarse iced cell spreads ice onto valley floors 2-3 km below it. Real valley glaciers do descend below the snowline (Franz Josef ends in rainforest at ~300 m), but only as tongues fed from above. Fix: accumulation only where the fine summer temperature is below freezing, with ice allowed to flow down valleys a limited distance (by flux / ice thickness) from there. Check on a zoom of a post-PW-102 world.

## Updates
- 2026-10-14: Created.
