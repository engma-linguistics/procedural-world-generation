---
id: PW-494
title: "Earth time zooms carve uniform rock (no rock record): use GLiM lithology for erodibility"
type: task
status: todo
parent: null
milestone: later
subsystem: timezoom
effort: s
impact: low
found_by: pw037-port
blocked_by: []
relates: [PW-037]
refs: [planet/timezoom/sources.py, tools/earth_data.py, data/earth/glim_L6.npz]
created: 2026-10-21
updated: 2026-11-03
---

## Description
`source_earth` has no `bedrock`, so on Earth the carving (PW-037) uses erodibility 1 and no sediment cover
everywhere. The shields (Canadian, Baltic) therefore carve like sedimentary basins, and the contrast that
makes the Great Lakes and Hudson Bay (soft Paleozoic rock beside the shield) can't appear.
`data/earth/glim_L6.npz` (GLiM lithology) is already cached:
- map its classes to `surface.ROCK_K` as `erod_base` (crystalline ~0.3, carbonates and shales 1-1.6);
- take the sediment cover from the unconsolidated classes.
- [ ] Earth zoom: erosion on the Canadian and Baltic shields is lower than on the Paleozoic platforms beside them

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: ice-age/time-zoom work, parked post-v1 (epic PW-470)
- 2026-10-26: Parent PW-037 (done) -> none. (PW-900 backlog reorg).
- 2026-10-21: Created from inbox draft draft-earth-timezoom-erodibility.md (found by pw037-port).
