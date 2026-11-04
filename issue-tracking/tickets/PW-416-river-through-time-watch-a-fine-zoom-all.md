---
id: PW-416
title: "River through time: watch a fine-zoom alluvial river migrate, cut off oxbows and avulse over ~5-10 kyr"
type: story
status: blocked
parent: PW-103
milestone: later
subsystem: zoom
effort: l
impact: low
found_by: daniel
blocked_by: [PW-412]
relates: [PW-094, PW-405]
refs: []
created: 2026-10-16
updated: 2026-11-03
---

## Description
Owner (2026-10-16): a deliverable for the floodplain work (PW-412): a fine-grained time view of a meander-capable river changing course, or whatever fits the reach (meander migration and oxbow cutoffs; delta or fan avulsion; braid-bar shifting). The glacial time zoom can't show it: its cells are ~56 km and its steps are kyr. This needs a time pass on a fine zoom (<=100 m/px, steps of ~10-50 yr over ~5-10 kyr). That is a first slice of PW-103's phase 3 (the last ~20 kyr), made for one region. Coordinator's lean: a kinematic centreline migration model (Howard-Knutson style: bank erosion from curvature with an upstream lag, neck and chute cutoffs leaving oxbow lakes, floodplain scroll bars and deposits). Use constant or slowly varying discharge, taken from the parent world or a glacial time zoom's climate where one exists. Output frames like a time zoom, with a viewer scrubber on the fine zoom's 2D/3D views. Keep the fine zoom's contracts at each frame (PW-389 block means apart from the migrating channel belt; exact fall/volcano heights). Blocked by PW-412: without floodplains, rivers have no room to migrate.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: zoom polish; zooms are good enough to read
- 2026-10-16: Owner 2026-10-16 late night: nice-to-have, NOT v1. Impact low; removed from the zoom-lane priority order.
- 2026-10-16: PW-412 done (157ac20). Hooks for the time pass: fine zooms now save valley_floor (0 none, 1 floodplain, 2 meander belt = channel width + 2x the train's amplitude each side, the whole floor on braided reaches, 3 the channel on the floor) and floor_m (the floor's surface, also under the channel: the level a vacated channel pixel fills to). stats.floodplain gives areas. The floor is held in the landscape pass and counted in the 3x3 means, so migrating the channel inside it moves volume only within the floor.
- 2026-10-16: Created.
