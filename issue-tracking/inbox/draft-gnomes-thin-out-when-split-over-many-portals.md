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
- 2026-10-30 (lane 78b, after merging niche learning; lane 77's suite, 4360a3, one try; main -> lane 78):
  - dnd seeds 7/10/13: 4.3 -> 3.7, 0.9 -> 5.0, 5.7 -> 5.5% (spread x6.7 -> x1.5); land 5-10 -> 11-13 Mkm²;
  - even_six 4.8 -> 14.7 and 3.2 -> 11.1; five_peoples 9.3 -> 15.7; goblin_world and mountain_stem level;
  - menagerie 5.0 -> 2.2 (one seed);
  - late_humans 8.1 -> 0.2: the humans land at 7 portals there (draft-arrivals-without-founders-land-at-every-portal).
  - So the regression lane 78 saw is gone on dnd once learning is in. Only the menagerie, at one seed, still shows it.
- [ ] pick an option (lean now: c, leave it); re-check menagerie at a second seed
