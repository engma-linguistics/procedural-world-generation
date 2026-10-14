---
id: PW-008
title: "History bookkeeping per cell: rift time, flat vs folded strata"
type: story
status: done
parent: PW-005
subsystem: tectonics
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: [planet/tectonics/events.py, planet/tectonics/crust.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Record per plate cell the facts the landform classifier needs: time since rifting (escarpment retreat
age), whether strata were folded/thrust in a collision or are still flat, flood-basalt eruption,
last glaciation. Plate-frame arrays, carried through checkpoints.

## Updates
- 2026-10-14: Status todo -> done. History in record.py: t_rift + rift_strain (ln beta), t_fold + fold_km + fold_strain (collisions, accretionary wedges), exhumed, t_ice; plate frame, in checkpoints. Branch landform.
- 2026-10-14: Created from the landform-classes epic (owner discussion 2026-10-14).
