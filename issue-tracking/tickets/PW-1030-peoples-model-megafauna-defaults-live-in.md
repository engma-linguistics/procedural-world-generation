---
id: PW-1030
title: "Peoples model: megafauna defaults live in three places and disagree; a \'head of cattle\' is 711 Mcal for dragons and 625 for giants; other constants are copies"
type: task
status: todo
parent: null
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-990, PW-992, PW-967]
refs: [planet/lineages/spec.py, planet/lineages/history/megafauna.py, planet/lineages/dragon_ages.py, planet/lineages/prey.py, planet/lineages/contacts.py, planet/lineages/salt_reach.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The dragon and giant settings have defaults written in three places that don't agree, and some explanations still describe the pre-ruling state ("candidates until the owner's review"). Dragons and giants are fed from differently sized cows. A handful of other numbers look shared but are copies that will drift.

From the lineages audit (spot-checked where marked): `Tree.dragon_ages = "base"` vs `DA.DEFAULT = "younger"` (parse uses the latter, so only directly built Trees get "base"); code default `dragon_generation = "schedule"` while both presets set "line" (PW-992); megafauna.py docstring still says `"prey" (default)` and spec.py:180 still says "candidates until the PW-967 review" (PW-967 is done; `MEGAFAUNA_NATURAL_DEFAULT = "food"` verified). Cattle: `dragon_ages.CATTLE_MCAL = 836 × 0.85` vs `megafauna.HEAD_KCAL = 625e3` (and the literal again at :401 with unnamed Kleiber `70 * M**0.75 * 1.7`). Copies: contacts.py `EST = 0.12` and `R_KM = 6371.0`, salt_reach.py's three "as seafood.X" constants, `ERAS` in spec.py and techtree.py. Tests toggle megafauna module globals by assignment (test_lineages.py:2358-2380).

Fix: the dataclass reads DA.DEFAULT/GENERATION_DEFAULT; fix stale docstrings; one `Head` record in prey.py; import the copied constants; a `MegafaunaParams` (BUDGET, FOOD_CAP, PEOPLE_PROD) so tests pass arguments. (Retiring the mesotherm/mammal modes and moving Seven Meals to "food" are owner questions, listed in the audit report.)

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-lineages-defaults-and-constants-drifted.md (found by code-audit-2026-10).
