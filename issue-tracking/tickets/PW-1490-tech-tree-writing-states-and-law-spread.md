---
id: PW-1490
title: "Tech tree: writing, states and law spread as fast as copper; nearly every people with hands holds the whole core ladder by the present"
type: task
status: needs-decision
parent: PW-661
milestone: later
subsystem: culture
effort: m
impact: med
found_by: scout-206
blocked_by: []
relates: [PW-1485, PW-1471, PW-1461]
refs: [docs/review/culture/techtree/spread1.md, docs/review/culture/techtree/spread1/measure.py, docs/review/culture/techtree/spread1/tables.py, docs/review/culture/techtree/spread1/tables_out.md, "planet/lineages/techtree.py::Calendar.advance", "planet/lineages/techtree.py::Calendar.can", "planet/lineages/techtree.py::contact_rate", planet/lineages/samples/techtree.toml, "runs 0141d1 3e0eb4 a2b637 07c755", "Murdock 1967 Ethnographic Atlas (D-PLACE EA028/EA033/EA055)", "Comin, Easterly & Gong 2010 AEJ:Macro 2(3)", "Svizzero & Tisdell 2015 Soc Evol Hist 14(2)"]
created: 2026-11-07
updated: 2026-11-07
---

## Description
**In plain words.** By the present-day finish, almost every people that has hands knows everything on the main ladder: metal,
cities, kingship, law and writing. That holds for about 95% of them (in Seven Meals, 45 of 48 peoples with hands) and for 98-100% of
the population. Writing goes from the first people to 9 in 10 peoples within about 1,000 years. Foragers and nomads know it too.
On Earth, around 1500 CE or the ethnographic present, things were far more uneven:
- **Farming:** about 1 culture in 5 had no farming.
- **Metal:** about half had no metal.
- **States:** only about 1 in 9 was a state.
- **By continent:** the Americas and Oceania scored 0.12-0.14 on Comin, Easterly and Gong's 1500 AD technology scale, against
  Europe's 0.87.

The full analysis is in docs/review/culture/techtree/spread1.md (scout 206, 8 draws on each of 4 runs). The baseline is main's tree
at 330b021b.

**What breaks or misleads if it is never done.** Every viewer page and brief that says "who knows writing, who has kings" will show
a world where everyone does. The slow, uneven spread that makes peoples differ is missing for exactly the techs that matter most to
cultures and polities.

**Causes, all measured.**
1. 505 of 552 techs share `spread = 1.0`. So writing, law and kingship cross a border at the Neolithic farming front's speed, as
   fast as copper.
2. Adoption checks only prerequisites, goods and body. The taker's way of life and density never gate it: foragers hold writing in
   70 of 80 people-draws in Seven Meals.
3. Every dnd people with hands has 9-37 neighbours now, so nobody is isolated.
4. A people holds a tech once any part of it does.

Causes 3 and 4 are features of the history and of the people unit. 1 and 2 are the tree's.

**Options.**
- **A: a sourced slow `spread` for the admin and urban techs** (writing, law, kingship, coinage, maybe cities): a fraction of the
  farming front. It needs a source for writing's or states' spread speed. None was fetched in spread1, so finding one comes first.
- **B: the taker must be settled enough to use the tech.** Admin techs are taken up only by a people with towns or chiefdoms
  actually in use, read from its way of life or its settlement ledger, not from the knowledge alone. That matches the Atlas:
  foragers with 2+ levels of authority are 3 of 291. This is a mechanism, not a number.
- **C: accept it at this scale.** A dnd people is a macro-people of millions, and weighted by population Earth in 1500 was ~99%
  non-forager. Show the unevenness inside a people instead (its regions, PW-1471) when the viewer needs it.

**Lean: B, then A if a source turns up.** B is a mechanism and leaves the fast, land-bound techs alone; those already look right.
Not v1-blocking.
- [ ] at the 0.5 kyr-ago state, the core admin techs (writing, kingship) held by clearly fewer peoples than the farming techs, on
  0141d1 and 07c755, over 8 draws
- [ ] the fast techs (crops, copper, iron) unchanged within draw scatter

## Updates
- 2026-11-07: Created from inbox draft draft-slow-techs-spread-like-crops.md (found by scout-206).
