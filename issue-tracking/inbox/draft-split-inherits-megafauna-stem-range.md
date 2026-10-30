---
title: A people split from a megafauna stem inherits the dragons' world-wide range at once (kobolds, dragonborn)
type: task
status: needs-decision
parent: null
milestone: v1
subsystem: timezoom
effort: s
impact: med
found_by: lane73
blocked_by: []
relates: [PW-677, PW-888, PW-937]
refs: [planet/lineages/history/origins.py, "peoples runs e6ca59 (lane 73 arm 2), 488d7e"]
---

## In plain words
When the kobolds branch off the dragons, they start out holding a large part of the land the dragons held, worldwide: 14.8 Mkm² on
three continents on day one, and 33 Mkm² once the dragon stem ends 50 kyr later. A new people should start in one region (or a few)
and spread from there. That is what the other splits do, because their parents are ordinary peoples with one region. Here the parent is a
handful of dragons scattered everywhere.

## Description
How splits found (origins._origin_split), general to every split:
1. The founders hold the suitable country within FOUNDER_KM of the origin cell.
2. If the origin falls in an isolated part of the parent's range (a component other than the largest), the founders take that whole part.
3. Polycentric founding (owner 10-27): up to POLY_MAX more patches of the daughter's own country inside the parent's range, one per
   POLY_MKM2 of the range.
4. When the stem ends at its last split (_end_parent, PW-677), each child takes the part of the stem's range nearest its own, and a part
   cut off from every child goes to the child that suits it best.

For a people stem these are local: the stem's range is one people's range. For the draconic stem, a megafauna line at a few dragons per
country, the range is every kind of dragon country on every continent. Rules 2-4 then hand a fully fledged people range to the kobolds and
dragonborn (non-megafauna), wherever dragons lived. That is why the kobolds held 55-60% of the dwarves' mountains in every owner run,
and why re-dating the kobolds to 350 kyr (lane 73) did not remove their lead.

Options:
- A. A non-megafauna child of a megafauna parent founds locally only: rule 1 plus polycentric patches (rule 3, within FOUNDER_KM each),
  with no whole-part takeover (rule 2) and no handover of the stem's remaining range at its end (rule 4). The dragons' range stays theirs.
  Small, in origins.py.
- B. The same for every split, so a stem's isolated parts end with the stem instead of passing to a child. This changes PW-677
  (owner-approved: the stem's isolated stock is its children's ancestors), so it needs the owner.
- Lean: A. The megafauna range is not a population of proto-kobolds.
- [ ] decide A or B; implement; re-run one peoples run and compare the kobolds' and dragonborn's founding area and present share
