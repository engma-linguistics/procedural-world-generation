---
id: PW-1011
title: "Settlements and cities v0, with lifecycles: sites rise when culture and tech allow, and fall (climate, rivers, peoples moving, later war), leaving ruins"
type: story
status: in-progress
parent: null
milestone: later
subsystem: culture
effort: l
impact: high
found_by: owner
blocked_by: []
relates: [PW-856, PW-910, PW-676]
refs: [planet/lineages/settlements.py, viewer/globe/settlements.js, docs/review/settlements/, "world 4360a3", "run 6553f1"]
created: 2026-10-29
updated: 2026-11-03
---

## Description
**In plain words.** Towns and cities that come and go. A site gets settled once a people's culture and technology allow it and the land supports it. It grows or shrinks with its people, climate and rivers, and can be abandoned: a river moves, rain fails, the people leave or are driven out, and later raids and wars. A place that held a city long ago may hold nothing today but a ruin, and a ruin can be resettled. Owner 10-29.

Design (coordinator):
- A settlement ledger of point records: cell plus a seeded sub-cell position; founded; population over time; who lives there and the minority quarters (PW-910, PW-889); abandoned and why; ruin.
- Stepped every ~50-100 yr over the last ~10 kyr, reading the history frames and climate frames interpolated in time.
- The globe shows dots; a regional zoom places each at km scale on its own terrain.
- Siting can start before fun lane 45b merges; sizes need its people density.
- Scout plan: docs/review/lineages/civ-scout.md candidate 2.

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: v0 shipped; the rest is not a must-have (status unchanged); polities v0 reads its ledger as it is
- 2026-10-30: Fun lane 60: v0 built. The settlement ledger (`planet/lineages/settlements.py`, output only: settlements.json + meta.settlements; `planet settlements RUN [--set K=V]`; written by every peoples run on a world) steps every 100 yr over the last 12.5 kyr. A cell's chief place is a village, town or city as its holder's techs allow (villages / towns / cities), sized as central places (village 2% of its cell's settled people, town 0.8% of cell + 1 ring and the best site of that ring, city 1% of 2 rings, likewise), x a site factor from harbours, navigable rivers, fresh water, soil and passes. It is abandoned to the sea, the ice, drought, 'the river moved away' (a seeded stand-in: 3%/kyr for lowland river sites), being driven out, or its people leaving; ruins stay and are resettled. Towns and cities draw their people from 1-2 rings (mixed), with city-minority quarters (PW-889). The viewer: 'Settlements and ruins' overlay, dots by holder and tier, grey crosses for ruins, along the time slider; hover card rows. Fixes on the way: 'villages' rate 0.12 (techtree.toml; it missed late_kyr, so peoples waited ~30 kyr; dwarves 12/16 -> 16/16 draws), and mining peoples (dwarves, kobolds) count HOLD_SHARE 0.5 of their heads as settled. World 4360a3 (seed 6001, L6), dnd seeds 7/8/9 (runs 6553f1, e368d1, 8d6884 vs main d050b2, 6319de, befbef: peoples' presence, layers and populations byte-identical): founded 8,354 / 9,071 / 8,440; alive now 7,665 / 8,182 / 7,824 (73-79 cities, 510-528 towns); ruins 689 / 889 / 616 (driven out 252-389, river moved 186-250, drought 81-122, people left 60-114, sea 9-14); humans hold ~70% of the living sites. ~55-59 sites per Mkm2 of peopled land; a 1 Mkm2 disc holds 61-91 places, 0-6 of them towns and 0-1 a city. 6 s per run. Screenshots: docs/review/settlements/. Follow-ups as drafts: rivers really moving, war and raids, zoom placement, minority holds (dwarves), the brief block, the late-chain cutoff.
- 2026-10-29: Created.
