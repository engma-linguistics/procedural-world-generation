---
id: PW-1531
title: "Faiths that come through towns stay small (a culture's towns hold ~2 % of its people): keep, add country migration, or soften the ruler's protection?"
type: task
status: done
parent: null
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lane223 (PW-1528; see also PW-1527)
blocked_by: []
relates: [PW-1520, PW-1489]
refs: ["planet/lineages/gods.py::Pantheons._towns", "planet/lineages/gods.py::protection", "planet/lineages/gods.py::urban_reader", docs/review/culture/faiths/mixing1.md]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: lane 223 (PW-1528) made a tolerant realm's towns take in the faiths of the realm's other cultures, and those faiths win
converts in the land about the towns. It works in the right direction and only under tolerant rulers, but it is small: the settlement
ledger puts a median of ~1.7 % of a culture's people in towns (90th percentile ~4 %), so a town quarter of another faith is a fraction of
a percent of the culture, and its spread to the countryside adds ~1-2 points to the share of tolerant-ruled cultures with a minority over
2 % (0141d1: 12.4 % -> 14.0 %, every one of six draws up; numbers for all three runs in mixing1.md). The share above 10 % does not move.
The large minorities of real tolerant empires (Syria's and Egypt's Christians) are the conquered peoples' old faiths, which the model
already keeps (conversion remnants, the ruler's shield from PW-1520).

Options:
- A. Keep it (lean): towns are where diasporas live, and a diaspora is a few percent; the visible "mixing" is in the Minorities tab's
  "came through towns" column and in more cultures holding small minorities.
- B. Add country migration inside a realm (colonists, resettlement: the Ottoman surgun, the Assyrian deportations), at a sourced rate,
  so minorities over 5-10 % can come from mixing too. A new mechanism, effort m.
- C. Soften the ruler's protection from the push's log scale (protection(0.7) = 0.28) to linear (0.7). Measured on 0141d1: the tolerant
  group's over-2 % share rises 12.4 -> 15.1 % (against 14.0 %), but intolerant-ruled cultures then gain too (9.4 -> 10.3 %).

What misleads if never decided: Daniel may read "tolerant rulers allow more intermixing" as large mixed populations and find only a few
percent.

## Updates
- 2026-11-08: Status needs-decision -> done. Daniel ruled D70 A 11-08: keep both as built (religious tolerance shields minorities; town-borne minorities). Regional pantheons (D68) add polytheist mixing on top.
- 2026-11-08: Folded into desk D70 with PW-1527 (both answer 'why don't minorities grow under tolerant rulers'). Lean A: keep.
- 2026-11-08: Created from inbox draft draft-town-faiths-small-at-ledger-town-shares.md (found by lane223 (PW-1528; see also PW-1527)).
