---
id: PW-978
title: Owner call on stem sapiens-node dates, then write them into the samples
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: sapiens-dates-doc
blocked_by: []
relates: [PW-971, PW-965, PW-947, PW-945]
refs: [docs/review/lineages/sapiens-dates.md, planet/lineages/samples/dnd.toml, planet/lineages/samples/seven_meals.toml]
created: 2026-10-28
updated: 2026-10-28
---

## Description
docs/review/lineages/sapiens-dates.md lays out candidate dates per stem (draconic, feline, goblinoid, hominid, avian). My leans: draconic 5 Myr, feline 2.0 Myr, goblinoid 1.2 Myr, hominid 1.7 Myr, avian 2.0 Myr, but these are leans for the owner to react to. After the owner's gut call, set `sapient` in dnd.toml and the draconic line in seven_meals.toml, and rerun the lineage tests.
- [ ] owner picks dates (see the doc's open questions)
- [ ] update the toml values and their comments

## Updates
- 2026-10-29: (fun-lane-44) Applied the owner's call in dnd.toml and seven_meals.toml: draconic node 5 Myr, feline 2 Myr, goblinoid 1.2 Myr, hominid stem 2 -> 4 Myr with node 1.6 Myr (~1.7 Myr of bare-bones tools first), giantkin 1.5 -> 1.1 Myr and true giants 1.2 -> 1 Myr, avian node 2 Myr; reptilian splits spread (lizardfolk 2.3, troglodyte 2.6, tortle 3 Myr; capped by an existing test, draft-reptilian-splits-capped-at-3-myr). Before/after table in docs/review/lineages/sapiens-dates.md (Applied PW-978).
- 2026-10-28: Owner 10-28 gut call on sapiens-dates.md: (1) adjust both the stems' timelines and what is allowed before sapience to reflect that real humans took ~3 Myr from first tools to sapiens (a long run of bare-bones tools before minds); (2) a node older than the first fossil is fine; (3) generation scaling is goofy for long-lived kinds, fine to ignore; (4) dragons ~5 Myr is plenty (can shift, whatever feels right); (5) giantkin must split earlier than 0.5 Myr after the hominid node: move dates or add an intermediate split as needed; (6) the reptilian peoples all split at about the same time: spread them out as feels reasonable; (7) goblinoids shorter in time than the hominids is fine.
- 2026-10-28: Created from inbox draft draft-sapiens-dates-owner-call.md (found by sapiens-dates-doc).
