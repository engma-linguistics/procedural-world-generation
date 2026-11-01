---
title: "Demes undersee dragons and giants: the frames keep only each cell's two leading peoples"
type: task
status: todo
parent: PW-670
subsystem: timezoom
effort: m
impact: med
found_by: lane108
blocked_by: []
relates: [PW-981, PW-670, PW-924]
refs: [planet/lineages/demes.py, planet/lineages/cultures.py, "runs cc22df 622c00"]
---

## Description
In plain words: dragons and giants rarely lead a cell. So they keep dropping out of the record the demes are cut from, and
then coming back. On cc22df the red dragons have 64 demes: 1 first deme and 63 that reappear after a gap. The fire giants
have 21. Round 2 handles this in the cultures: a cohesive kind's returning pockets rejoin its first culture. But the demes
themselves, their contacts and the Demes tab still show the churn.

Candidate fix: cut megafauna demes from the history's own pockets (PW-924 scatter) or from a megafauna presence layer,
instead of from peoples_whole, mix_lead and mix_second. This needs a look at what the frames store. Lane 101 owns history/.
