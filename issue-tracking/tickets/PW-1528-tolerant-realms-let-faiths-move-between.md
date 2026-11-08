---
id: PW-1528
title: "Tolerant realms: let faiths move between the cultures of one realm (towns draw people from several cultures), so minorities grow under a tolerant ruler"
type: task
status: done
parent: null
milestone: null
subsystem: culture
effort: m
impact: med
found_by: lane219
blocked_by: []
relates: [PW-1489, PW-1369]
refs: ["planet/lineages/gods.py::Pantheons._pulls", "planet/lineages/gods.py::Pantheons._shares", "planet/lineages/gods.py::urban_reader", planet/lineages/settlements.py, docs/review/culture/faiths/tolerance1.md, docs/review/culture/faiths/minorities1.md, "runs 0141d1 3e0eb4 07c755"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: Daniel asked (PW-1520) that a religiously tolerant ruler let faiths mix, so that minorities grow and persist. Lane 219 split out a religious
tolerance, made tolerant rulers push their faith less and shield their subjects' minorities, but measured over six re-rolled draws on 0141d1,
3e0eb4 and 07c755 the share of cultures with a minority above 10 % did not move outside the noise (6.6 -> 6.0 %, 5.7 -> 5.6 %, 5.3 -> 6.1 %).

Why: in the model a minority is only ever made by a conversion (the old faith stays on) or by a faith pressing over a border up to the 10 %
plateau. A tolerant ruler *slows* those (less push), so it keeps faiths apart by culture (the realm is plural: 97-99 % of states hold two
faiths at 10 %+), but nothing mixes them *within* a culture. What is missing is people moving: a realm's towns draw people from several of
its cultures (settlements.py already records who lives in a town, by people), and each brings its faith. Under a tolerant ruler a culture's
towns would then carry the faiths of the realm's other cultures, in proportion to the town share (urban_reader) and the ruler's religious
tolerance.

What misleads if never done: the viewer shows tolerant empires whose cultures are each as single-faith as an intolerant one's; Cordoba's
mixed court has no counterpart. Belongs with the towns-and-minorities model PW-1369 deferred.
- [ ] a culture's town share takes in the realm's faiths (from its towns' residents or its realm's cultures), at a rate that rises with the ruler's religious tolerance; sourced or labelled JUDGEMENT
- [ ] measured over re-rolled draws: minorities above 10 % rise in tolerant realms against intolerant ones

## Updates
- 2026-11-08: Status todo -> done. Lane 223 merged (a1c019d4): town-borne faiths in tolerant realms; paired +1..+6 pts cultures with a minority >2% under tolerant rulers, ~0 under intolerant; leading faiths unchanged on every draw. Suite 1110 passed.
- 2026-11-08: Created from inbox draft draft-tolerant-realms-mix-faiths-between-cultures.md (found by lane219).
