---
id: PW-1238
title: "disease_resist is in the spec (dwarves 0.75) but nothing scales by it yet: the plague code (PW-1167) must read it"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: timezoom
effort: xs
impact: med
found_by: lane97
blocked_by: []
relates: [PW-1192, PW-1167, PW-1194]
refs: [planet/lineages/spec.py, planet/lineages/samples/dnd.toml, planet/lineages/history/counter.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** Lane 97 gave every people a "disease resistance" (owner D25: dwarves shrug off three quarters of plague losses and
still carry plague). The number is stored and passed down the tree, but the history has no plague yet, so today it changes nothing.

- Built (lane 97): `Lineage.disease_resist`, 0..1, default 0; splits and groups inherit it, a hybrid takes its parents' mean; dnd dwarves
  (and hill dwarves) 0.75. The owner's 0.75 is read as "resists 75% of plague losses", i.e. a loss L becomes L x (1 - 0.75). If he meant
  "takes 0.75 of the losses", the number should be 0.25.
- To do with PW-1167 (plague pulses and the pandemic era): scale each plague pulse's loss and the era's recurrence hazard by
  (1 - disease_resist); keep carrier status unchanged (a resistant dwarf crowd still carries the disease along its trade roads).
  Lane 82's `plague_x` is not built, so nothing to replace.
- [ ] the plague code reads disease_resist; a test that 0.75 leaves a quarter of a pulse's loss
- [ ] shown on the peoples tab beside the life history (PW-1192's last box)

## Updates
- 2026-10-31: Created from inbox draft draft-disease-resist-needs-the-plague.md (found by lane97).
