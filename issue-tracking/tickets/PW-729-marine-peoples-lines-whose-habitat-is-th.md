---
id: PW-729
title: "Marine peoples: lines whose habitat is the sea (deep folk on trenches and vents, merfolk on the tidal interface, storm giants offshore)"
type: story
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: l
impact: med
found_by: culinary-intake
blocked_by: []
relates: [PW-188, PW-692]
refs: [planet/lineages/history.py, planet/lineages/spread.py, planet/coastal.py, docs/proposals/culinary-dnd-intake.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Every lineage lives on land cells today. Swimmers and fliers cross the sea but settle on land. The owner's world
has an aquatic clade:
- merfolk, a coastal-interface people whose pantry is the tide pools;
- deep folk ("sea elves"), with no fire, vent cooking, brine curing and a vent intoxicant;
- storm giants, offshore and barely in contact.

Add `realm = "sea" | "coast" | "land"`:
- **sea lines** take habitat on sea cells by depth band, water temperature, light, upwelling, reef and kelp, and
  vents (ridge and arc volcanism from the tectonics), and spread through the sea graph;
- **coast lines** hold the sea and land cells of the coast;
- they compete with each other, not with land peoples. Contact with land peoples happens on the shared coast, for the
  contact record and the brief.

Outputs: presence on sea cells, the peoples layer at sea, stories, and the brief (vent access for deep folk is food,
heat and intoxicant at once).

Option B, if the cost bites: coast lines only, with the deeps authored by the culinary side, who say they "couldn't
visit" there anyway. The lean is A for merfolk and storm giants.
- [ ] Measured cost at L7.
- [ ] Land peoples' numbers unchanged.

## Updates
- 2026-10-24: Created from inbox draft draft-marine-peoples.md (found by culinary-intake).
- 2026-10-24: fun14 did not start this (budget went to PW-756); code pointers and the lean are in draft-marine-habitat-not-started.
