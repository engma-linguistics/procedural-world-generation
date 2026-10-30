---
title: The peoples editor has no fields for a line's way of life, realm, megafauna kind, mass, group size or rivalry
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: fix-lane-49
blocked_by: []
relates: [PW-1033, PW-795, PW-723]
refs: [viewer/lineages.html, planet/lineages/spec.py, planet/lineages/run.py]
---

## Description
In plain words. You can set these things on a people in the tree files, but the peoples editor in the viewer shows no box or menu for them, so you can't see or change them there: way of life (`way`: forager, farmer, pastoral nomad...), realm (`realm`: land, coast or sea, PW-795), megafauna kind (`megafauna`), body mass (`mass_kg`), group size (`group_size`) and `rivalry`.

PW-1033 (fix lane 49) made the editor take its option lists from `GET /api/lineage-schema` (`planet/lineages/run.editor_schema`). The schema already sends `ways` and `realms`, so the two menus need no new copied lists. Adding the fields is new editor UI, which was out of scope for that fix lane. Check spec.py's parse for each key's valid values and whether it is inherited, then add the fields in the line panel next to traits, in the same style (an empty value means inherit or default).
- [ ] way and realm menus built from the schema
- [ ] megafauna, mass_kg, group_size, rivalry inputs; empty means the default
