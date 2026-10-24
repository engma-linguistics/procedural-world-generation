---
id: PW-727
title: Contact history per pair of peoples by epoch, interfertility tiers from split depth, substrate (who held a cell before), and Tier-1 clines carrying body shares across a border
type: story
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: culinary-intake
blocked_by: []
relates: [PW-103, PW-701, PW-661]
refs: [planet/lineages/history.py, planet/lineages/compose.py, "culinary-dnd docs/genetics.md", docs/proposals/culinary-dnd-intake.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
The culinary repo's genetics doc rests on two facts: who lives next to whom, and how deep their split is.
`meta.present` has neighbours only at the present.

**Contact record.** Per pair of peoples, per stored epoch:
- border length and mixing share;
- first contact (the first epoch their ranges touch);
- the total years in contact;
- the corridor kind (river, coast, open lowland, closed);
- stored in `meta.contacts`.

**Interfertility tier.** From the depth of the last common ancestor, with tree-meta thresholds (default T0 under
10 kyr or same people, T1 under 1 Myr, T2 under 40 Myr, else T3). Fae arrivals are T3 with all. Overlays (★) are
interfertile with their hosts. The half-elf exemption (✦) is marked by hand. Per-pair overrides go in the tree. In
the brief and the stories: "humans and orcs: T1 sister species, in contact for 11 kyr along 2,400 km".

**Substrate.** Per cell, the people that held it (presence ≥ 25%) before its present leader, and until when. This is
the canon's "substrate vocabulary": the strait empire's food words for wild foods are loans from the people who were
there first.

**Clines.** Between T1 neighbours, body shares (PW-701, e.g. milk) diffuse across the shared border with a small
rate. That makes the culinary ruling "the milk line runs through the orc side, not along the border" an output.
- [ ] Measured on two worlds.
- [ ] Wish score and empty land unchanged (output only), except the cline layer.

## Updates
- 2026-10-24: Created from inbox draft draft-contact-history-and-interfertility-tiers.md (found by culinary-intake).
