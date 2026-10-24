---
id: PW-733
title: "Find a world for a written setting: score candidate worlds on setting requirements (rain-shadow steppe, inner sea with a strait, desert belt, volcano coast, tea highlands to an eastern delta, island arcs) and keep the best"
type: story
status: todo
parent: PW-692
milestone: later
subsystem: highlights
effort: m
impact: med
found_by: culinary-intake
blocked_by: []
relates: [PW-692]
refs: [planet/highlights.py, docs/proposals/culinary-dnd-intake.md, "culinary-dnd docs/world-map.md"]
created: 2026-10-24
updated: 2026-10-24
---

## Description
The owner wants to "find a planet with cool continents" to run the ice-age pass, the finest time pass and the
peoples on. Their culinary repo stalled on authoring a map whose constraints fight each other (proposal §1, §3.1).

Make a tool, `tools/world_fit.py` or `planet fit`, that reads a requirements file (TOML: `must` and `nice` items,
each with a weight) and scores a finished world. The requirement kinds are built from highlights and existing
layers:
- an enclosed or semi-enclosed sea with a narrow strait into a second sea (new: a strait finder, sea cells whose
  removal splits a sea basin);
- a dry steppe in a north–south range's lee;
- a desert belt and savanna and equatorial forest in sequence;
- a volcano within N km of that sea;
- a river from wet highlands to a delta on another coast;
- island arcs or chains at given latitudes;
- a trench;
- a wet mountain flank;
- a closed-basin salt lake between forest and steppe.

It reports each item's score, the place found, and a total. Over a batch of runs and moments (L6 for the search,
then L7 for the pick), it lists the best worlds.

Leans on Q1 of the proposal (the sim's world is the map). The requirements file for the owner's world is a rewrite
of their master reference §3. The culinary side writes it.
- [ ] Works on existing showcase worlds.
- [ ] Earth scores well on "Mediterranean with a strait" as a sanity look.

## Updates
- 2026-10-24: Owner 2026-10-24: procgen owns the map; no fitting worlds to the culinary repo's written geography. Moved to later; a 'find a cool-looking world' search can reuse it.
- 2026-10-24: Created from inbox draft draft-world-fit-for-a-written-setting.md (found by culinary-intake).
