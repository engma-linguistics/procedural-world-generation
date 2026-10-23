---
title: Arrivals from outside the world (elves, gnomes, tritons) land on one landmass only
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fill2
blocked_by: []
relates: [PW-683]
refs: [planet/lineages/history.py, planet/lineages/samples/dnd.toml]
---

## Description
An 'arrival' people is placed at one best-habitat site, so it begins on one landmass and must cross seas like anyone else (elves have sea share 0.3, gnomes 0.1). Options: (A) leave it (one portal; the sea crossings decide), (B) found it on the best site of each of the N largest landmasses ("the Feywild opens in several places"), (C) a `places` list per arrival in the preset. PW-683 asked for this. After the pioneer fix (fill2) far continents fill from any landing, so (A) is no longer what leaves land empty; my lean is A.
