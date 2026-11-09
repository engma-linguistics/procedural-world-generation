---
id: PW-1243
title: War-torn land (lane 82's K(W)) is built as a brake with one dial (meta.war); PW-1172's war deaths, era dials, troubles and refugees are still open
type: task
status: todo
parent: PW-917
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane97
blocked_by: []
relates: [PW-1172, PW-1165, PW-1194]
refs: [planet/lineages/history/counter.py, planet/lineages/history/params.py, docs/review/peoples-brakes/report.md]
created: 2026-10-31
updated: 2026-11-09
---

## Description
**In plain words.** The owner's D25 A (land as the general brake) is in: crowded, stateless peoples next to enemies lose some of their
land to war (fields left unworked, people pulled back to strongholds). It is lane 82's formula, with one viewer dial "how warlike the
peoples are" (meta.war, x0 to x4). At x1 it is small: the late human farmers live in states and lose a few percent of their land; tribal
gardeners and herders lose more. What PW-1172 still asks for is not built:

- war deaths through the life tables (excess over the schedule's own violence, stage weights 0.1/0.3/1/0.3, MALE_W);
- separate early and late dials (`war_early` / `war_late`) and a per-line `war_x` and the `aggressive` trait's x2;
- seeded "times of troubles" pulses (Turchin's cycles);
- refugees: land lost to war adding to a people's crowding, so it jumps;
- the state term reads tech level x the people's farm share (a judgement standing in for its town share).

Lane 97 also built the shared K channel lane 82 designed (PW-1165's `kept`, as `CounterMixin._brake`), without its `lost` output in
the run file and workbench (only the stress suite records it, as `brakes`).
- [ ] PW-1172 builds on `history.counter` instead of a second channel
- [ ] the run output and the workbench show each people's lost-to shares (war, raid, feud, cull)

## Updates
- 2026-11-09: Lane 259: run output per line lost_to {war, feud, raid, cull, all} + troubles + refugee_jumps (history.summary); workbench 'land lost' column in Peoples today; stale lost shares cleared when no brake acts. State term keeps the farm share in the stand-ins (town share exists only with live polities, which read the ruling tier).
- 2026-11-03: Milestones 11-03: later -> v4: v4 must-have: folded into PW-1172's war in the history
- 2026-11-03: Triage 11-03: v2 -> later: war, plague, events and life-history belong with the v3 civilization epic (PW-661); not needed for a first culinary brief
- 2026-10-31: Created from inbox draft draft-war-land-term-built-rest-of-war-open.md (found by lane97).
