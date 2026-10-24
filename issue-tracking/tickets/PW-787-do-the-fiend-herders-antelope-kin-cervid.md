---
id: PW-787
title: Do the fiend herders (antelope-kin, cervid-kin) milk their animals at all? Owner call; default is that herders milk
type: task
status: wontdo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun20
blocked_by: []
relates: [PW-784]
refs: [planet/lineages/animals.py, planet/lineages/samples/seven_meals.toml, planet/lineages/spec.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-784 made dairy come from the dairy animals a people keeps x its way of life (herders milk); lactase (`body.milk`) now only
decides fresh vs fermented. A body key `milks = false` says a people does not milk at all (default true). On 6fbc2c (run eaf863)
the antelope-kin (lactase 0), the cervid-kin reindeer herders (0) and the Arha (0.1) therefore all show **fermented** dairy
(yogurt, kefir, kumis, cheese) from horse, goat and cattle, because the `seven_meals` tree sets no `milks`.

Options: (A) leave it: all herders milk, the fiend herders ferment it (the real steppe pattern); (B) set `body = { milk = 0, milks = false }`
on the antelope-kin and/or cervid-kin so their herds give meat, blood and fibre but no dairy (a lore choice: fiends who feed on
the herd rather than from it); (C) give the antelope-kin dairy but not the cervid-kin. Lean: A until the owner says otherwise.
- [ ] Owner picks; then add `milks = false` to the chosen lines in `seven_meals.toml` (and dnd.toml if wanted) and re-run the showcase.

## Updates
- 2026-10-24: Status needs-decision -> wontdo. Owner ruled 2026-10-24: fiend-kin milk by default; no line gets milks=false.
- 2026-10-24: Created from inbox draft draft-fiend-herders-milk.md (found by fun20).
