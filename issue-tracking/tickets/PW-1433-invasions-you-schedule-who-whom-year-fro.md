---
id: PW-1433
title: "Invasions you schedule: who, whom, year, from where, how hard, with an 'it happened / it didn't' read-out"
type: task
status: done
parent: null
milestone: v3
subsystem: peoples
effort: l
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-756]
refs: []
created: 2026-11-03
updated: 2026-11-04
---

## Description
In plain words: an invasion row nudges the history in that window and place; an editor in the workbench; the existing incursion detector (contacts.py) reports how far it got. Plan: docs/review/board/milestones-v2-v5.md.

## Updates
- 2026-11-04: Status todo -> done. Lane 177 merged: States & war tab, rows in authored.json, read-out per row, sim incursions listed. Strong rows with a bordering state happened 7/7 on a2b637; most windows lack one (PW-1450).
- 2026-11-04: Lane 175 left the polities hook: planet/lineages/polities.py::derive(invasions=[{who, whom, from_kyr, to_kyr, strength}]) raises war_v0's chance x2/x4 (strong waives the odds) and logs how='invasion' in the conqueror's 'took'; feed it from the run's authored rows and add them to server.polities_doc's cache key. docs/review/culture/polities/round2.md.
- 2026-11-03: Created.
