---
title: "Faiths: 77 of 108 faiths forbid swine and faiths are founded up to 300 kyr ago, so every myth reads alike and older than its language"
type: task
status: todo
parent: null
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-lane5
blocked_by: []
relates: [PW-1537]
refs: ["runs/a24559/languages.json (faiths: taboos, founded_kyr)", "planet/language/texts.py::myth", "planet/language/texts.py::TABOO_CONCEPT", "planet/lineages/gods.py", "planet/lineages/cuisine.py::_taboos", "tools/language/sketch.py::faith_section"]
---

## Description
In plain words: the cold review (PW-1537 R3 and R6) found that every demo myth forbids wild swine and that faiths are
"founded 300 kyr ago", fifteen times older than any proto-language in the run (20 kyr). Lane 5 varied the myth's wording
per faith (verb of the god lines, the invocation) and now says when a people took a faith over from another, but the
content comes from the faith data, which is thin and uniform: on a24559 the divine food taboos are swine 77, carrion
birds 25, sea beasts 3, waterfowl 3, eels 2, shellfish, wheat and cattle 1 each, across 108 faiths (53 have one taboo,
27 none). With swine in seven faiths of ten, the myth section reads as one template whatever the wording.

What misleads if never done: a reader of any two demo myths sees the same pig taboo and an impossible age, and takes
the faith model as boilerplate.

What to try: on the lineages side, draw divine taboos from the god's own domain more widely (a sea god's fish or
seals, a hunt god's game, a herd god's cattle or milk, a forest god's deer; the swine-forest link is one of many,
Simoons 1994 *Eat Not This Flesh*), and cap or explain `founded_kyr` against the founding culture's own age (or print
"older than the languages now spoken" instead of a number).
- [ ] no divine taboo target held by more than ~30% of faiths on a24559
- [ ] the sketch never prints a founding date older than the run's proto-languages without saying so
