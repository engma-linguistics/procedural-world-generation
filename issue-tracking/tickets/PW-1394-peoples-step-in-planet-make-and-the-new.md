---
id: PW-1394
title: Peoples step in `planet make` and the New planet form (and a real run kind for peoples runs)
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: m
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-1209, PW-481]
refs: ["docs/review/fresh-eyes/2026-11-03.md#2-recommendations-ranked", planet/make.py, planet/lineages/output.py, viewer/]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: the one-command path that builds a planet (`planet make`) stops at the zooms, so a person using the viewer has to run the peoples step by hand with the command line; the owner uses the viewer, not the command line. Add a peoples step to the make chain (planet/make.py:5-14) and a matching choice on the New planet form. Peoples runs are also still stored as `kind: timezoom, phase: lineages` (planet/lineages/output.py:161); give them a kind of their own so a peoples run is not mistaken for an ice-age time zoom (the subsystem split of 11-03 did the same on the board).
- [x] `planet make` builds a peoples run after the world (an option, a preset choice such as dnd or seven_meals)
- [x] the New planet form offers it
- [x] a peoples run has its own kind in the store; old runs deleted, no compatibility path (repo rule)

## Updates
- 2026-11-03: Created.
- 2026-11-03: Lane 153: `planet make --peoples TREE` and the form's peoples choice (planet/make.py, viewer/start.js); peoples runs are kind `peoples` (no phase) in the store, family, API and viewer. Existing runs are relabelled by the one-off tools/relabel_peoples_runs.py, run by the coordinator after merge (then delete it). Follow-ups: draft-navigator-peoples-tree-choice, draft-peoples-stage-time-estimate.
