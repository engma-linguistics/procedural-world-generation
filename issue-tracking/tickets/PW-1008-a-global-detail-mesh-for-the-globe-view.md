---
id: PW-1008
title: "A global detail mesh for the globe view: terrain synthesized at L9-L10 from the run's own records, consistent with the zooms"
type: task
status: todo
parent: PW-1198
milestone: v2
subsystem: viewer
effort: m
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-516]
refs: [docs/review/landscape/world-orogen.md]
created: 2026-10-29
updated: 2026-10-29
---

## Description
World Orogen draws terrain on a separate render mesh of up to 2.5M cells, synthesized from its tectonic records (belt geometry, crest size, roots) plus noise, about 1 s per frame on 8 workers. We could do the same for the globe at full view: upsample a world's L7 fields to L9/L10 with synthesized detail driven by our records (belts, volcanoes, rivers, rock), cosmetic only, never fed back into the physics. It must agree with what a regional zoom builds at the same place (same seeds and forms), or it lies. Weigh against just showing zooms.

## Updates
- 2026-10-29: Created.
