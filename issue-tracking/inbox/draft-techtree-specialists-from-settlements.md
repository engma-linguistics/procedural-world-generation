---
title: "Tech tree: a people that only knows of cities by contact counts as a city people (specialists 10%); read the settlement ledger instead"
type: task
status: todo
parent: PW-946
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-64
blocked_by: []
relates: [PW-946, PW-1011]
refs: [planet/lineages/techtree.py, planet/lineages/settlements.py, planet/lineages/samples/techtree.toml]
---

## Description
In plain words: the tree decides how many of a people are craftsmen and scholars from the techs it knows. Knowing "cities" counts as
having them, even for a band of 1,500 hill giants who heard of cities from a neighbour.

In v1, the specialist share s (the [[specialists]] ladder) is read from a people's own known techs: villages 0.5%, farming 1-2%,
towns 5%, cities 10%. Techs spread by contact, so a small people bordering a city people gets s = 0.10. Run 6128a3, seed 0: hill
giants (1.5k), goliaths and firbolgs know towns or cities. It does them little harm today, because their pool (N x s) stays under the
threshold. But it is wrong for mid-sized peoples.

The settlement ledger (settlements.py, PW-1011) knows who actually holds towns and cities and how many people live in them. It can't be
read today, because it is built after the tech tree and from it (its tiers come from meta.techtree.known). Options:
- A: only a tech the people invented, or held for some kyr, counts for the ladder (cheap, still a proxy).
- B: step the tree and the ledger together (PW-946), with s = the share of the people living in towns and cities at the time.
Lean: B, as part of PW-946; A as a stopgap only if PW-946 slips.
