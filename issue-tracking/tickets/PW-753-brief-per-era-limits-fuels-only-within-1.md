---
id: PW-753
title: Brief per-era limits - fuels only within 12.5 kyr, groups seen only where strongest, route has no "wing", salt/fish uses (PW-745) not started
type: task
status: todo
parent: PW-692
milestone: later
subsystem: food
effort: s
impact: low
found_by: fun12
blocked_by: []
relates: [PW-742, PW-745]
refs: [planet/lineages/landuse.py, planet/lineages/history.py, planet/lineages/brief.py]
created: 2026-10-24
updated: 2026-11-03
---

## Description
Left after PW-742's remainder:
- Fuels per era are recomputed only for frames within `landuse.ERA_WINDOW_KYR` = 12.5 kyr (the land use's inputs are stored as uint8 `eraq_*` layers
  for those frames); older eras print the present's fuels flagged. Widening costs ~6 x frames x cells bytes; or thin to the brief's default era slices.
  The crops' `know`/`straw` at a frame treat every known stock as fully grown (no per-frame growth range), so era 0 differs a little from `planet fuels`.
- `groups_best` stores only the strongest group per cell, so a group beside a stronger sister group (or minor) is invisible in the brief's per-era groups.
- `route`: origin / road / sea are recorded (layers `route_<stock>.bin`); `wing` (carried by birds) has no mechanism in the spread.
- PW-745 (salt trade reach, salting works, [[use]] rows for the sea-food goods) was not started: it changes habitats (golden, physics) and has judgement calls.
- Landuse inputs are written twice (`landuse.derive` for the present, `frame_inputs` per frame): a refactor to share them is worth a yes.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: culinary follow-up of low weight; the core brief and cuisine tickets stay in v2
- 2026-10-24: Created from inbox draft draft-brief-era-window-and-route-wing.md (found by fun12).
