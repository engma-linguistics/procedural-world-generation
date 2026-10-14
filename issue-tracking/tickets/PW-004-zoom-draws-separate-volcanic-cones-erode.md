---
id: PW-004
title: Zoom draws separate volcanic cones, eroded old islands and atolls
type: story
status: done
parent: PW-001
subsystem: zoom
effort: l
impact: high
found_by: daniel
blocked_by: [PW-003]
relates: []
refs: [planet/zoom.py, planet/zoom_kernels.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Given the world's volcano list, the zoom synthesises each volcano: a cone (stratovolcano for arcs,
shield for hotspots) sized by height and age, gullied and lowered as it ages, and once an ocean island
has subsided in warm water (SST > ~20 °C), a fringing reef → barrier reef → atoll sequence. Arc chains
should read as separate peaks, not a ridge.

## Updates
- 2026-10-14: Status in-progress -> done. Done. Zooms e8fa0e (chain), 4e6647 (atolls, 1 km), 122cc1 (eroded islands, 1 km) of world a099c6; zoom.json stats.volcanoes lists each with its form. Arc density and continental calderas left as inbox drafts.
- 2026-10-14: zoom_volcanoes.py: shields with rift lobes and calderas, stratocones, eroded tops with radial valleys, guyots, fringing/barrier reefs, atoll rings with motu; province replaces the coarse terrain near vents so channels are sea. Young cones pinned through the landscape pass.
- 2026-10-14: Status todo -> in-progress. Started in worktree volcanoes.
- 2026-10-14: Created from the discrete-volcanoes epic (owner discussion 2026-10-14).
