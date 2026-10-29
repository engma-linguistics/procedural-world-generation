---
id: PW-981
title: "Demes: phylogeography pass that cuts each people's range into speech/breeding populations per frame and tracks their splits, fusions and contacts into a dated deme tree"
type: story
status: todo
parent: PW-856
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: owner
blocked_by: []
relates: [PW-767, PW-902, PW-731, PW-665]
refs: [planet/lineages/contacts.py, planet/lineages/spread.py, planet/lineages/crossing.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Owner 2026-10-28 (design talk, no code yet). Foundation for every language path (faked or first-principles) and likely for PW-856's cultures. Today a people is one presence field over its whole range (humans on three continents = one blob) and groups split by way of life, not geography; no cell records which earlier population its people came from.
Output-only pass over the stored frames, like contacts.py:
- per frame, cut each people's occupied cells into demes by travel cost (corridor and sea-gap machinery from crossing.py) and isolation by distance (a connected continental range becomes a dialect chain, not one community);
- link demes across frames by overlap; newly settled cells at an expanding front take the label of the cell they spread from (spread.nearest_label may do most of it), giving founder chains;
- record splits, fusions, extinctions and deme-to-deme contact intensity over time; ice-age land bridges opening and closing should show up.
Result: a dated, located deme tree nested inside the authored people tree, plus a contact series per deme pair. Caveats: time resolution is the frame spacing (kyr in the glacial zoom); ancestry is inferred from range change; diffusive spread smooths fast corridor migrations.
- [ ] on a fantasy run, a widespread people splits into several demes along real barriers, with dates, and the tree is stored in run meta
- [ ] a review page/map of demes over time

## Updates
- 2026-10-28: Owner 2026-10-28: moved under the cultures epic PW-856 and into v2 (cultures are probably demes more than species); still the foundation of the language work under PW-767 and of the demo PW-986. Strongly tied to PW-902 (ranges follow ice-age sea level and land bridges).
- 2026-10-28: Created.
