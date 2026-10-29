---
title: "Demes pass costs 70-110 s per L7 peoples run: cut it to seconds by working on each people's own cells"
type: task
status: todo
parent: PW-981
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun46-demes
blocked_by: []
relates: [PW-981]
refs: [planet/lineages/demes.py, "run b69f51"]
---

## Description
In plain words: the new demes pass runs after every peoples run and adds a minute or two (b69f51: 71 s; ac4c06: 112 s)
to a ~6.5 minute job. Most of that is whole-globe array work repeated per people per frame, though a people holds a
small part of the globe.

Profile (b69f51, 129 frames x ~25 peoples): Demes._cut ~45 s own time (whole-grid numpy masks and BFS/Dijkstra over
163,842 cells for every people and frame), _diameters ~11 s. Fix: per people per frame, compact its cells plus the sea it
crosses into a local subgraph (index map + local CSR) and run the kernels there; skip peoples whose occupancy changed
by only a few cells (relabel the changed cells only).
- [ ] demes.derive on b69f51 under 15 s with identical output (test on the demes.json)
