---
id: PW-1082
title: Owner review of the 'among' pairs, the city-minority shares and the PW-889 constants (all design judgements)
type: task
status: todo
parent: PW-692
milestone: later
subsystem: culture
effort: xs
impact: low
found_by: fun-lane-54
blocked_by: []
relates: [PW-889, PW-665, PW-856]
refs: [docs/review/lineages/kinship-cities/README.md, planet/lineages/samples/dnd.toml, planet/lineages/history/params.py, planet/lineages/history/cities.py]
created: 2026-10-30
updated: 2026-11-03
---

## Description
In plain words. Fun lane 54 added two things to the dnd preset. First, some peoples are happy to live inside a friendly people's
country ("among"). Second, goblins and kobolds now keep a small minority in other peoples' towns. Every number behind these is a guess
made by the lane, not a measured fact. All of them can be edited in the lineages editor (Wishes tab: the pair wish "among"; Peoples tab:
a group's "lives in other peoples' cities" box and "share of the townsfolk"). Please look over the list and change anything that feels
wrong for the setting.

Preset data (dnd.toml):
- among wishes: bugbears among goblins (1.0) and among hobgoblins (1.0), goblins among hobgoblins (0.8), halflings among humans (0.8),
  gnomes among dwarves (0.6)
- city goblins: 3% of the townsfolk; city kobolds: 2%; both since 5 kyr ago, the hosts being every other people present

Constants (history/params.py, each commented as a judgement):
- AMONG_TOLERANCE 0.7: how much an among wish softens the pair's competition
- INTEGRATE 0.5, SQUEEZE_FILL 0.5: how far a people squeezed out of its country is willing to live among a friendly neighbour
- CITY_TOP 0.05, CITY_MIN_KM2 5: the towns are the densest twentieth of the peopled land (at least 5 people per km2)
- CITY_REACH_KM 1000: a city minority lives only in towns within 1000 km of its own people's country

- [ ] owner: keep, change or drop each among pair; set the city shares (should kobolds also live in dwarven towns only, say?)

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: later cultures work (languages, polities, religion, morality); food comes first (fresh-eyes review, D44)
- 2026-10-30: Owner 10-30: goblinoid cohabitation confirmed. City minorities generalise: any people that doesn't usually get along with a city's or polity's people can live there as a minority if it 'promises to play nice' (tolerated, dirty looks). Kobolds and goblins were only examples. Build once polities exist.
- 2026-10-30: Created from inbox draft draft-among-pairs-and-city-numbers-owner-review.md (found by fun-lane-54).
