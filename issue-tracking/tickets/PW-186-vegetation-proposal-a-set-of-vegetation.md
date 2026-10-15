---
id: PW-186
title: "Vegetation proposal: a set of vegetation types (owner: >=30, <<2000) as layered per-cell variables, for owner review"
type: story
status: in-progress
parent: PW-184
subsystem: surface
effort: s
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner: wants a proposal before the model. Plants are not individually tracked: per-cell fractions of a set of types (2D arrays), like the plant functional types of dynamic vegetation models (DGVMs use ~10-20 PFTs). Owner bounds: no fewer than ~30 types, well under ~2000. Propose: a core of ~15-20 functional types (tropical evergreen / raingreen broadleaf trees, temperate broadleaf deciduous, temperate and boreal needleleaf evergreen / deciduous, C3 and C4 grasses, shrubs by climate, tundra forbs/mosses/lichens, succulents, wetland/peat plants, mangroves, seagrass/kelp for coasts) crossed with structure/phenology to give ~40-80 named vegetation types for maps and games; the rules for productivity (light, warmth, water: an NPP model), competition and cover, fire, and the feedbacks (albedo, evapotranspiration via the Budyko/evap_cool path, soil carbon); compute cost; Earth checks (MODIS land cover, NPP). Write as docs/proposals/vegetation.md for the owner.

## Updates
- 2026-10-14: Status todo -> in-progress. Coordinator: the ticket was only the brief; an agent (worktree vegprop) is writing docs/proposals/vegetation.md for owner review.
- 2026-10-14: Created.
