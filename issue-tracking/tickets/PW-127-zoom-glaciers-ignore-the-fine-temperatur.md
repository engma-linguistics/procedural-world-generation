---
id: PW-127
title: "Zoom glaciers ignore the fine temperature: ice drawn on warm valley floors"
type: task
status: done
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
- 2026-10-14: Status todo -> done. Fixed in 9efe11f (zoomice). Glaciers come from each pixel's own climate (zoom.glaciers, earth.ice_sheets' rule): accumulation where the summer at the pixel's height (world ice-surface temps undone to bare ground, coarse ice's own cooling back on) is below ice_summer_temp and snow outlasts the melt; surplus routed down valleys as melting tongues (0.8 km wide at 0.1 km3/yr, cap 3 km3/yr, 100 km). f724bd at 3.41,-38.65 (81f0f6's spot, seed 2): ice px with mean T > 0 C 41% -> 5%, > 5 C 30% -> 1%, p90 16.8 -> -2.1 C; ice elev p10 427 -> 2427 m; ice share of land 50.5 -> 32.0%. Sheets stay sheets: 800c99 74,-178 largest component 100 -> 99% of ice (zoom 516056); 67317b 64,-18 97.2 -> 99.8% of land iced. Mid-latitude range 800c99 -44.7,-72 (zoom d2a1d5): 0 -> 10.9% of land in icefields and valley glaciers, p10 3325 m, tongues to ~1600 m. Images docs/review/ice/. Leftovers in inbox (temperature layer near ice, viewer, snowline judgement call, stale 81f0f6).
- 2026-10-14: Created.
