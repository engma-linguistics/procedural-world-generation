---
id: PW-187
title: "Vegetation model: type fractions, productivity, fire and feedbacks (per the approved proposal)"
type: story
status: done
parent: PW-184
subsystem: surface
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-14
updated: 2026-10-15
---

## Description
Implement the approved vegetation proposal on worlds (and in run keyframes if cheap; the run already has a veg cover term used for weathering). Feeds soils (organic matter), biomes (replacing the Koppen lookup's role in the map), the viewer ('satellite view', PW-083) and later species placement.

## Updates
- 2026-10-15: Status in-progress -> done. Steps 1-4 merged (veg): planet/vegetation.py, 19 PFTs, 61 named types, fire, stand ages, run equilibrium feeding erosion/weathering, evolving plant groups with slider ticks. Demo run 732abb (L7, seed 3199), world 351f32; Earth world fe2af4. Steps 5-9 continue as PW-214 (zoom), PW-203 (feedbacks), PW-213 (time zoom), PW-212 (soils), PW-206 (game attributes).
- 2026-10-14: Coordinator: world bcc894 (and finished bcb4b6) show east-west stripes of forest/grassland across the southern continent's interior in the biome map (Whittaker threshold on a banded rain field?). The vegetation map should not inherit them; check there.
- 2026-10-14: Status todo -> in-progress. Agent started in worktree veg: steps 1-4 (with PW-194 monthly climate builder and PW-195 Earth data) plus the evolving plant groups and timeline ticks.
- 2026-10-14: Proposal approved; build per docs/proposals/vegetation.md sections 9.1 (steps) and 9.3 (owner decisions). Notable: 19 land PFTs (mangrove/salt marsh moved to PW-188); evolving plant groups with timeline ticks in the viewer; rain recycling as the last feedback.
- 2026-10-14: Created.
