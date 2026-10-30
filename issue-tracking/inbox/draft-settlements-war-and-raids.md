---
title: "Settlements: sacked, razed and walled: war and raids as a cause of a site's fall"
type: task
status: todo
parent: PW-856
milestone: v2
subsystem: timezoom
effort: l
impact: med
found_by: fun-lane-60
blocked_by: []
relates: [PW-1011, PW-661, PW-961]
refs: [planet/lineages/settlements.py, planet/lineages/contacts.py]
---

## Description
In plain words. Towns and cities in v0 (PW-1011) fall when the sea or the ice takes them, the rain fails, a river moves, or their people leave. When a different people takes over the land, the ledger records a change of hands ("held by the humans since ~2.1 kyr ago"). It calls a site "driven out" only if the newcomers keep no villages. There are no battles: no town is sacked, no city walled, no raids from giants or dragons.

What to try, reading what the runs already store:
- the contact record's incursions (meta.contacts, with direction and dates);
- the 'fortifications' tech;
- the megafauna (PW-961: raids, tribute).

Then:
- a site on a front with an incursion has a chance to be sacked (it shrinks) or razed (it becomes a ruin, "razed by the orcs");
- walls (fortifications) halve that chance;
- dragons and giants raid towns in their country.

Owner (PW-856, 10-25): crowding on a small landmass leads to conflict over resources. This belongs to the civilization epic.
- [ ] a "sacked by" and "razed by" reason in the ledger, from stored contacts; walls matter
