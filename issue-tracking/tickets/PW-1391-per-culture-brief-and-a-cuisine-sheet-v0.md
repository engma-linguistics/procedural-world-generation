---
id: PW-1391
title: "Per-culture brief and a cuisine sheet v0: answer 'what does this culture cook' before languages and polities"
type: story
status: needs-decision
parent: PW-856
milestone: v2
subsystem: food
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-692, PW-1312, PW-905, PW-744]
refs: ["docs/review/fresh-eyes/2026-11-03.md#2-recommendations-ranked", "planet/lineages/brief.py::build", docs/review/cultures-proposal/proposal-r2.md, docs/review/lineages/showcase-peoples/briefs/]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: the project's end goal is a book of what each culture eats and cooks, but the brief still answers "where is this species", not "what does this culture cook". Cultures are the unit of the book (decisions 10-25, PW-856), yet `brief.build(run_ref, region, people, era_kyr)` (planet/lineages/brief.py:248) takes no culture, and the cuisine is a few if/else notes in `_suggested` (brief.py:1099-1150, `"drink": None`). The culinary repo's five questions are fuel, staple, drink, who eats together, and what outsiders get wrong; drink and who-eats-together have no model at all. The fresh-eyes review (R1) asks to do this before languages (PW-982 ff) and polities.

Needs Daniel (desk D44.1): do food and the cuisine sheet go first, ahead of languages and polities? Lean (reviewer and coordinator): yes.

Scope if yes (effort M):
- brief takes a culture (and place and era); the cultures proposal r2 puts the brief last (docs/review/cultures-proposal/proposal-r2.md section 7).
- Move `_suggested` into a new `cuisine.py`; give it a drink and a who-eats-together line.
- Fold in PW-1312 (food taboos per culture), PW-905 (food fit as a biology spectrum), PW-744 (cuisine plants are markers only).
- Regenerate or delete the brief_version 7 samples in docs/review/lineages/showcase-peoples/briefs/.
- [ ] Daniel decides the order (D44.1)
- [ ] one culture's cuisine sheet v0 for a showcase people

## Updates
- 2026-11-03: Created.
