---
title: "Zoom temperature layer: ice-free pixels next to coarse ice inherit the ice's cooled surface"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomice
blocked_by: []
relates: [PW-127, PW-101]
refs: [planet/zoom.py, "zoom d2a1d5", "zoom 516056"]
---

## Description
Since PW-127 the zoom decides its glaciers on the bare ground's temperatures (ice_ground() undoes climate.ice_surface per coarse cell), but the `temperature` layer and the Koppen/biome classes still use the world's ice-surface temperatures, Gaussian-interpolated and reduced with the bedrock height only. So a valley that is now ice-free beside a coarse ice cell shows that cell's cooled surface (its height, its white-top cooling, the melting cap), and a new alpine glacier in a coarse ice-free cell gets no ice cooling at all. Fix: build the fine temperature from the bare-ground fields (gw_sl / gc_sl and an annual equivalent) and apply climate.ice_surface on the final glacier mask with the pixel's own ice thickness. Changes the Koppen EF and biome near ice; check zooms d2a1d5 (-44.7,-72, 800c99) and 516056 (74,-178, 800c99).
