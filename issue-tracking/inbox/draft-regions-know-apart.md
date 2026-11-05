---
title: "Tech tree: a people's regions invent apart but still know as one (knowledge and contact per region)"
type: task
status: todo
parent: PW-661
milestone: later
subsystem: culture
effort: l
impact: med
found_by: lane-200
blocked_by: []
relates: [PW-1471]
refs: ["planet/lineages/techtree.py::Calendar.learners", planet/lineages/demes.py, docs/review/culture/techtree/round1.md]
---

## Description
**In plain words.** With region learners (D55), each continent of a people gets its own chance to invent. Once one region invents,
though, the whole people knows the tech at once, on every continent. Contact is still people to people too. The faithful version
keeps knowledge per region: the other regions learn it over the people's own internal front, or by contact with a neighbour on
their own continent. That needs region-level contacts (demes.py has deme-pair contacts after the run) and polities that read their
own region's knowledge, so it touches the polities and the viewer's tech tab.

**What breaks if never done.** Humans on a far continent "write" the moment their kin overseas do. A polity there can then be a
state without any local writing.
