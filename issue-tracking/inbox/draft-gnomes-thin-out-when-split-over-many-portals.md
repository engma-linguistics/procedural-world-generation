---
title: Gnomes end rarer when their founders are split over many portals
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: highlights
effort: s
impact: med
found_by: lane78
blocked_by: []
relates: [PW-1150, PW-1149]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/history/portals.py]
---

## In plain words
When the gnomes come through portals, their founders are split into 6-7 small groups. They end up with fewer people than when they all arrived as one group at their best place:
- one roll went from 4.5% of the world's people to 3.1%;
- another went from 2.3% to 0.9%.

They do hold about as much land, or more. Elves, by contrast, gain a lot from arriving in force: from 0.06% to 0.5% of people on one roll, and from 0.28% to 0.44% on the other.

## Description
- Measured on world 4360a3 at L6, seeds 7 and 10, 2 tries each, comparing main against lane 78's on-state:
  - base: fdac7f and ad0a2d;
  - on: 35ab55 and d1b5e3.
- The gnomes' 4e6 founders are split across every portal they can live near. On seed 10, one portal could hold only part of its share (3.3 M carried of 4 M).
- Each small patch is then contested in full country. The gnomes' growth rate is x0.46 of the humans', so they recover slowly.
- Options:
  - (a) the gnomes get `portals = 2` or `3`, a few strong landings;
  - (b) one wave per portal, staggered;
  - (c) leave it, since canon has gnomes few and scattered.
- [ ] pick an option; screen gnomes' share on lane 77's suite
