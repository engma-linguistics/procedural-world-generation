---
id: PW-971
title: Let a stem's sapiens node gate its language and techs, and mark it in run results
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-42
blocked_by: []
relates: [PW-965, PW-868, PW-945, PW-947]
refs: [planet/lineages/spec.py, planet/lineages/techtree.py, viewer/lineages.html, planet/lineages/samples/dnd.toml]
created: 2026-10-28
updated: 2026-10-28
---

## Description
PW-965 added the dated sapiens node (`sapient = "T"` on a stem) and the "continues as animals, untracked" end (`animals = true`), both as markers: they do not change the simulation or the tech tree. Two follow-ups, deliberately left out:

- The tech tree (techtree.py) still lets language arise per stem from its own earliest date. A stem's techs could be gated so nothing arises before its sapiens node (dragons: 4 Myr in the samples). This touches language dates, which the owner has parked (PW-947, "language is a later joint project"), so it waits for that ruling.
- The node dates for feline, avian, goblinoid and hominid stems in dnd.toml are placeholder guesses (between the stem's start and its first split); the dragon date (4 Myr) is also a guess. The owner should set them, or ask for sourced values.
- The Results tab and run timelines (from a stored run's `meta.tree`) do not draw the node or the animals tail yet; only the Tree tab does.

- [ ] decide whether sapiens gates language/techs (needs PW-947)
- [ ] draw the node and the animals tail in the Results/run views

## Updates
- 2026-10-28: Created from inbox draft draft-sapiens-node-gates-language-and-lairs.md (found by fun-lane-42).
