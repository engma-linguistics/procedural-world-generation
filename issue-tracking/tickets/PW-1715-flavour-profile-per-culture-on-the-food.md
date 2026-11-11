---
id: PW-1715
title: "Flavour profile per culture on the food sheet: salty, sour, umami, fat, heat, smoke, sweet, bitter, funk, each with its reason"
type: story
status: todo
parent: PW-692
milestone: v1.0
subsystem: food
effort: l
impact: high
found_by: plan-v1-lane
blocked_by: []
relates: [PW-905, PW-744, PW-1391, PW-722, PW-732]
refs: [docs/review/plan/milestones-to-v1.md, planet/lineages/, viewer/lineages.html, PW-692, PW-1391, PW-905]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: the end goal (PW-692) asks what each people eats and how it tastes. The food sheet already answers what (crops, herds, fuels, salt, fish), but nothing yet says how a kitchen tastes.

If it is never done, the culinary book has inventories and no flavour. The "how it tastes" half of the end goal stays a blank the owner fills by hand for every culture.

Build a profile on nine axes (salty, sour, umami, fat, heat, smoke, sweet, bitter, fermented funk) from data that already exists:
- salt distance and salting works (PW-732, PW-745);
- fuels: dung and peat give low, smoky fires (PW-722);
- spice, capsicum and sugar crops (PW-738, PW-765);
- dairy and fat from herds (PW-835);
- ferments (PW-744);
- the people's senses: who tastes capsaicin, sweet, lactase (PW-905).

Each axis shows its reason, for example "smoke: high, dung fires on the steppe". The weights stay visible and are either sourced or labelled as invented; this is not tuning toward taste. The profile shows on the food sheet and in the brief.

Proposed for v0.6.0 (docs/review/plan/milestones-to-v1.md section 5, #1).

- [ ] Every culture of a Seven Meals run has a profile with a reason per axis, and steppe herders, forest farmers and coast fishers come out visibly different
- [ ] The brief's JSON carries the profile, with a schema note

## Updates
- 2026-11-11: Created from inbox draft draft-flavour-profile.md (found by plan-v1-lane).
