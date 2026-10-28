---
title: Owner call on stem sapiens-node dates, then write them into the samples
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: sapiens-dates-doc
blocked_by: []
relates: [PW-971, PW-965, PW-947, PW-945]
refs: [docs/review/lineages/sapiens-dates.md, planet/lineages/samples/dnd.toml, planet/lineages/samples/seven_meals.toml]
---

## Description
docs/review/lineages/sapiens-dates.md lays out candidate dates per stem (draconic, feline, goblinoid, hominid, avian). My leans: draconic 5 Myr, feline 2.0 Myr, goblinoid 1.2 Myr, hominid 1.7 Myr, avian 2.0 Myr, but these are leans for the owner to react to. After the owner's gut call, set `sapient` in dnd.toml and the draconic line in seven_meals.toml, and rerun the lineage tests.
- [ ] owner picks dates (see the doc's open questions)
- [ ] update the toml values and their comments
