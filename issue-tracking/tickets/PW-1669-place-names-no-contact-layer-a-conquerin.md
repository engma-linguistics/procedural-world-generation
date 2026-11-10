---
id: PW-1669
title: "Place names: no contact layer (a conquering or trading people's generics never enter the local habit: no Danelaw -by)"
type: task
status: todo
parent: PW-767
milestone: v5
subsystem: culture
effort: m
impact: med
found_by: lang-lane15
blocked_by: []
relates: [PW-1658, PW-1636]
refs: ["planet/language/placenames.py::Habits._drift", "planet/language/history.py::loan_kinds", planet/language/contact.py, "scratch pass a24559 (lane 15)"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: lane 15's naming habits are inherited down the family tree and drift by chance (a generic falls out of
use, a new one comes in, one grows commoner). A habit never takes a generic from a neighbour, so a region ruled or
settled by another people keeps a clean family map. On Earth the contact layer is often the most visible thing on the
map: Danelaw -by and -thorpe in England, Norman 'Mont-' and 'Beau-', Arabic 'Guad-' (wadi) river names in Spain. PW-1658
asked for it ("a contact layer, as lane 13's elite/trade profiles"); lane 15 left it out. What misleads if never done:
conquest and long trade leave loanwords (lane 13) but no trace on the map, so a conquered region's places read as if
nothing happened.

Try: in `Habits.habit`, when a lect has an elite or trade donor (history.loan_kinds / lane 13's contact kinds) with pull
above a threshold, adopt one of the donor's generics into the habit (weight by pull), borrowed as the donor says it
(names._hear), noted in the habit's `changes` ('took up -by from the d123 rulers').
- [ ] a24559: at least a few lects under elite rule carry a donor generic in their settlement names

## Updates
- 2026-11-10: Created from inbox draft draft-place-name-contact-layer.md (found by lang-lane15).
