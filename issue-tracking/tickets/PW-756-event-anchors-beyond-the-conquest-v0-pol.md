---
id: PW-756
title: "[[event]] anchors beyond the conquest v0: polities (ruled-by valence), derived incursions, direction, and the culinary-repo events"
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun13
blocked_by: []
relates: [PW-730, PW-731, PW-734, PW-661]
refs: [planet/lineages/reputation.py, planet/lineages/spec.py, planet/lineages/samples/seven_meals.toml, docs/proposals/culinary-dnd-intake.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Built with PW-730 (v0): `[[event]] kind = "conquest", by, over, at, strength?` is parsed (`reputation.parse_events`, `Tree.events`, round-trips
through `to_raw`) and read by the reputation pass as a `feared` candidate for each overrun people in contact with the conqueror now, with the
legend row's memory (`memory_kyr`). No place is stored: the owner (PW-734) says the conquerors' origin is the world's. Why it was needed: on world 1df1c3
the sim's own substrate takeovers gave no conquest by either fiend people (small peoples among 80 Mkm2 of humans), so without an anchor nobody
called them devils or demons. What is left:
- **polities** (S ruled O: the old cervid-led polity over a human majority, intake 4.5): needs a `resented` valence and its category rows. The preset
  models it today as a second conquest (cervid-kin over humans, 3 kyr), which overstates it. Owner has not ruled on the polity.
- **direction** ("the devils who came down from the steppe to the west"): the row's text names no direction yet; centroids or highlights.
- **derived incursions**: a people's presence rising sharply in another's cells within a few centuries (PW-661's thin slice).
- an event is not yet placed on the map or shown in the brief's `events` (those are the run's own); the cells the conquerors held are not nudged.
- [ ] `resented` valence and a `polity` kind
- [ ] direction in the reputation text
- [ ] the viewer's tree editor keeps `[[event]]` rows when it saves a tree (it only knows lineages, wishes and uses today)

## Updates
- 2026-10-24: Created from inbox draft draft-event-anchors-parsed-and-stored.md (found by fun13).
- 2026-10-24: fun14: built derived incursions (contacts.Contacts.incursions into meta.contacts.incursions; reputation reads them before authored events, which stand only where none was found; rows carry from_dir and the text names the direction) and a herder press (spec.WAY_PRESS). On 1df1c3 neither fiend people conquers by displacement, so the authored events still carry the devils and demons. Left: polities and the resented valence, viewer tree editor keeping [[event]] rows, co-residence incursions (draft-incursions-by-co-residence).
