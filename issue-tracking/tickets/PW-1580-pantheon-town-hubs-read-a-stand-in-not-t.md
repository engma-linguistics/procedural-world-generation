---
id: PW-1580
title: Pantheon town hubs read a stand-in, not the towns' mixed peoples over time
type: task
status: todo
parent: PW-1308
milestone: null
subsystem: culture
effort: m
impact: low
found_by: lane236
blocked_by: []
relates: [PW-1523]
refs: ["planet/lineages/pantheons.py::Regional.step", "planet/lineages/pantheons.py::HUB_URBAN", "planet/lineages/pantheons.py::HUB_MIX", planet/lineages/settlements.py, "planet/lineages/gods.py::urban_reader", docs/review/culture/faiths/pantheon1.md, "run 0141d1"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** A regional pantheon can gather around a mixed trading town (PW-1523). The design asks for a town where two or
more peoples have each lived for centuries. settlements.json stores who lives in each town only for the present ("who" "now"), so v0
uses a stand-in. The hub culture must have at least HUB_URBAN of its people in towns, and at least HUB_MIX of its border must face
other peoples' cultures, both for HUB_KYR. That stand-in is a border town, not a town shown to be mixed.

If this is never done, a town hub can form where the town itself held one people, and a truly mixed port on a one-people coast never
forms one. On the stored D&D runs nearly every pantheon is an empire hub; town hubs are rare (0-2 per world). So the Pantheons tab
undersells the trade-city case, which is the main case in the sources (Delos, Alexandria).

Fix: store a coarse `who` series per town in settlements.json (for example every land-use frame, top 3 peoples with shares). Then
the town hub tests the town's own mix for HUB_KYR, as the design says.

## Updates
- 2026-11-09: Created from inbox draft draft-pantheon-town-hub-who-series.md (found by lane236).
