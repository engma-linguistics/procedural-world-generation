---
id: PW-838
title: Flat map defaults to the Equal Earth projection
type: task
status: done
parent: null
milestone: v2
subsystem: viewer
effort: xs
impact: low
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Owner: the default flat map view should select Equal Earth.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 24 (de83743).
- 2026-10-25: fun-lane-24: proj.name defaults to equal-earth; the URL carries proj= only when it differs (proj=equirect is now explicit); 3D relief still takes the live equirect map. The projected maps draw no overlays: draft-flat-map-projections-lack-overlays.md.
- 2026-10-25: Created.
