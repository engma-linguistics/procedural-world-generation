---
id: PW-1152
title: A people split from a megafauna stem inherits the dragons' world-wide range at once (kobolds, dragonborn)
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane73
blocked_by: []
relates: [PW-677, PW-888, PW-937]
refs: [planet/lineages/history/origins.py, "peoples runs e6ca59 (lane 73 arm 2), 488d7e"]
created: 2026-10-30
updated: 2026-11-03
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

## Updates
- 2026-11-03: Status needs-decision -> done. Closed 11-03 (housekeeping, fresh-eyes review s3): built. One-spot founding is the rule for every split (owner D20 'no inherited worldwide ranges', 10-31, decisions.md): origins._origin_split founds at one spot, origins._origin_off_megafauna handles the dragon stem; overview 2.26 'One-spot founding'.
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-split-inherits-megafauna-stem-range.md (found by lane73).
