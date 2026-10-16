---
id: PW-334
title: "Earth world: the terrain-only rock map makes every shelf shale, so warm carbonate shelves turn muddy and lose their reefs"
type: task
status: done
parent: null
subsystem: coast
effort: s
impact: low
found_by: coast-batch
blocked_by: []
relates: [PW-323, PW-188]
refs: [tools/earth_world.py, planet/coastal.py, tools/coastal_check.py, docs/review/audit/coast-batch.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`tools/earth_world.earth_rock` builds Earth's geology from the terrain alone: every sea cell above -1000 m is SEDIMENT under 2 km of cover, with SHALE at the surface. Since PW-323, coastal.turbidity stirs up the bed's mud on shallow tidal or wave-swept shelves wherever the floor is a soft, fine sediment (coastal.soft_floor: not HARD_ROCKS such as LIMESTONE, not SANDSTONE). On Earth this makes the warm carbonate shelves muddy, although their real floors are carbonate sand with little fluff. Earth L6 coastal_check: reef 466,000 -> 123,000 km2 (observed ~250,000-285,000). GBR 53,000 -> 7,000 (its reef cells at a median 18 mg/L; observed mid-shelf ~1-2), Arafura 66,000 -> 8,000, Indonesia 179,000 -> 55,000. Generated worlds lay down LIMESTONE where the run's reefs grow (tectonics/earth.reefs: sea at least reef_temp, little river mud), so they lose less (a seed-11 L6 world: 414,000 -> 288,000 km2, mostly shallow shale tidal flats).

Diagnostic (not committed): with LIMESTONE on Earth's shelf cells (above -1500 m) whose annual SST is at least reef_temp and whose river turbidity is under 3 mg/L, the same rule as the run's, Earth's reef comes back to 404,000 km2 and seagrass sits at 744,000 (1.02 million before PW-323, 309,000 with the all-shale map).

Fix: in earth_rock, put LIMESTONE at the surface of the warm shelves by the run's own reef rule (the world's SST and the rivers' mud, so it needs the climate first, or a second pass in build()), rather than a carbonate map of Earth. Keep the rest of the terrain-only rock map.
- [ ] Earth's warm shelves carbonate by the run's rule; coastal_check reef within ~2x of observed

## Updates
- 2026-10-16: Status in-progress -> done. Done (2108bf1): Earth world built twice; second pass sets LIMESTONE on warm clear shelves (SST >= reef_temp, river mud < 3 mg/L, -5..-1500 m). coastal_check reef 130k -> 386k km2 (obs 250-285k), seagrass 324k -> 710k, GBR 2.2k -> 14.7k. Earth world build ~2x slower.
- 2026-10-16: Status todo -> in-progress. Agent started.
- 2026-10-16: Created from inbox draft draft-earth-rock-map-carbonate-shelves.md (found by coast-batch).
