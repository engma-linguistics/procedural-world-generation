---
id: PW-602
title: "Lineages: review the contact-corridor values and the mixing share on more worlds"
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: lineages-lane-2
blocked_by: []
relates: [PW-601, PW-649]
refs: [planet/lineages/crossing.py, planet/lineages/history.py, docs/review/lineages/showcase-2.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Mixing at the present means cells where at least 2 native lines each hold at least 25%. With one try each it fell from 38-45% of the land under lane 1 to 17-34% now:

| world | lane 1 | lane 2 |
|---|---|---|
| 119973 | 58 Mkm2 | 27 Mkm2 |
| 81aced | 74 Mkm2 | 57 Mkm2 |
| c00ebf | 61 Mkm2 | 24 Mkm2 |

Corridor land (contact >= 0.7, ~10% of the land) is 25-66% mixed; closed land is 10-17% mixed. Most of the remaining mixing is on open lowland (contact 0.5), between peoples with little niche overlap (e.g. dragonborn with hobgoblins or humans), plus the human-halfling farmland, which the preset asks for.

The values are first guesses:
- crossing.corridor: rivers 0.9, coasts 0.8, plains 0.5, other 0.3
- ALPHA_CLOSED 1.4
- same_way: x0.5 per difference in way of life

- [ ] look at the showcase maps (docs/review/lineages/) and decide whether plains should mix less (contact 0.4) or rivers more
- [ ] the river field is the world's present flow, used for all glacial and recent epochs, so rivers on shelves exposed at low sea level are missing; deep epochs have no rivers

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: Created from inbox draft draft-lineages-corridor-tuning.md (found by lineages-lane-2).
- 2026-10-23: Lineages lane 3 addressed the shelf item. Exposed continental shelf at a low stand (land in a glacial or recent epoch, sea at the present) now gets a contact value of at least 0.7 (crossing.SHELF_CONTACT), standing for the coastal plains and lower river courses missing from the present-day flow field. Deep epochs still have no rivers: the plates have moved since.
  - Plains (0.5) and rivers (0.9) are left unchanged. The L7 showcase (showcase-3.md) mixes 11-21% of the land: 21-42% in corridors, 6-17% in closed land. Nothing there argues for a change, so the decision stays open.
