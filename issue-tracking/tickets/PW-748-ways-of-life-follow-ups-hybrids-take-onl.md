---
id: PW-748
title: Ways of life follow-ups - hybrids take only the first parent's way, no preset line is a sea nomad or horticulturalist, way weights are first guesses
type: task
status: todo
parent: PW-103
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: fun10
blocked_by: []
relates: [PW-723, PW-724, PW-661]
refs: [planet/lineages/spec.py, planet/lineages/samples/dnd.toml, planet/lineages/landuse.py]
created: 2026-10-24
updated: 2026-11-03
---

## Description
PW-723 landed `Lineage.way` (spec.WAYS). Left over:
- A contact hybrid or half-people takes its first parent's way (half-orcs are farmers, as humans), where the trait union used to give humans' fertile and orcs' grazing rows together. Decide whether a hybrid should blend its parents' ways (e.g. agro_pastoral) or keep the first.
- sea_nomad and horticulturalist exist in the table but no dnd.toml line uses them (the real mode has no sea-nomad group; tortles and lizardfolk could be horticulturalists or fisher-foragers). Add them where the owner wants them, with a sea-nomad group of seafarers.
- The weights in WAYS (transhumant grazing .7 + fertile .3, fisher_forager fish 1 ...) are first guesses; the transhumant herders now hold 31% of the world's best farmland on 3e9e7d (before: 0), nomads 33 Mkm2 (23). Judge on several re-rolled draws before tuning.
- Hill giants are pastoral nomads but there is no giant-scale stock yet (PW-724), so they tame the ordinary herd animals at density 0.01.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-10-24: Created from inbox draft draft-ways-of-life-followups.md (found by fun10).
