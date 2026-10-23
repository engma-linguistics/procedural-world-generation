---
id: PW-662
title: "Peoples change the land: farmland clearing, deforestation, pasture and fire use around settled peoples"
type: story
status: todo
parent: PW-103
milestone: v2
subsystem: surface
effort: l
impact: med
found_by: daniel
blocked_by: []
relates: [PW-650]
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24) asked whether peoples affect the land (farmland, cutting down forests). Today they don't: humanuse.py's 'fertile' rates farmland potential, and the lineages pass reads it, but nothing writes back. A first, modest version (not a history generator): from PW-650's populations and each people's way of life (agricultural, pastoral, forest), derive an anthropogenic land-cover overlay at the present and the recent pass's last few kyr: cleared cropland on fertile land near dense farming peoples, pasture and burned grassland around herders, managed or cut forest near timber users, settlement density. Shown as a world layer and in the vegetation's satellite colours; optional feedback onto the zoom's plants. The heavier historical version (soil exhaustion, collapse, megafauna) belongs with the civilization epic.

## Updates
- 2026-10-23: Created.
- 2026-10-24: First version built (planet/lineages/landuse.py, `planet landuse`, viewer land-use layer and tint; see docs/proposals/lineages.md "Peoples change the land"). Runs d489d0 (1df1c3) and 7709bf (3e9e7d): cropland 0.7% / 1.3% of the land, forest lost 1.5% / 2.5%. Open: drafts anthro-feedback-zoom-plants, anthro-land-per-person (needs-decision), anthro-tint-world-satellite.
