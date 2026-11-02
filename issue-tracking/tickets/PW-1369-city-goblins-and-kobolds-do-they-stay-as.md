---
id: PW-1369
title: "City goblins and kobolds: do they stay as groups now that peoples have none? (Daniel to confirm)"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: lane 136 / lane 137 (density ladder build)
blocked_by: []
relates: [PW-1357, PW-1275]
refs: [planet/lineages/samples/dnd.toml, "planet/lineages/samples/dnd.toml (city_goblin, city_kobold: origin = group)", docs/review/peoples/density-ladder/build.md, docs/review/cultures-proposal/owner-notes-r1.md, docs/review/cultures-proposal/owner-notes-r2.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: you ruled that peoples have no groups (PW-1357): ways of life now come from the land and what a people knows, so
"human farmers", "steppe orcs" and the like were removed. Two entries are still groups in the D&D preset: city goblins and city kobolds
(`origin = "group"`, `group_of = goblin / kobold`), small minorities living in other peoples' towns. Lane 136 kept them because they
are not a way of life (not farming, herding or foraging) but a place in someone else's society.

Options:
- (A) keep them as groups: the only groups left, and only for town minorities (they say something the ladder cannot);
- (B) remove them: goblins and kobolds in towns would wait for a later towns and minorities model;
- (C) turn them into an overlay (a share of their host's people, like other overlays) rather than a group.
Lean A.

## Updates
- 2026-11-02: Status in-progress -> done. Merged 15fb88b9: city_goblin/city_kobold and the city-minority mechanism removed (history/cities.py etc.); trees naming cities/hosts are refused with a pointer here. Town minorities: new draft intaken.
- 2026-11-02: Daniel 11-02 confirmed: drop them.
- 2026-11-02: Status needs-decision -> in-progress. Daniel 11-02 asked whether this means a group for every minority anywhere (dozens). It would: groups don't scale to minorities. Coordinator call (he deferred): B, remove the two city groups; town minorities wait for a towns and minorities model.
- 2026-11-02: Created from inbox draft draft-city-minorities-groups.md (found by lane 136 / lane 137 (density ladder build)).
