---
id: PW-1192
title: "Per-people disease resistance (disease_resist 0..1, inherited like the body): dwarves 0.5 halve their plague losses but still carry plague"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane-85
blocked_by: []
relates: [PW-1167]
refs: [docs/review/peoples-events/design.md, planet/lineages/spec.py, planet/lineages/samples/dnd.toml]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** In D&D dwarves are tough against poison ("You have advantage on saving throws against poison, and you have
resistance against poison damage", 5e Dwarven Resilience, roll20 compendium, read). The owner (10-31) wants that to carry over to
plague and epidemics. Design: docs/review/peoples-events/design.md, section 3.

- **The field.** `disease_resist` is a float 0..1 on a `[[lineage]]`, default 0. Splits and groups inherit it as a body key (like
  `limits`), and a hybrid takes its parents' mean.
- **What it scales.** The plague pulse's loss and the pandemic era's recurrence hazard (PW-1167), each × (1 − resist). With lane 82's
  table, dwarves in struck towns keep 86% instead of 71% at the recurrence hazard.
- **What it leaves alone.** Carrier status, famine, war, and growth rates.
- **Lane 82's `plague_x`.** This replaces it. Undead and constructs: 1.
- **dnd.toml.** dwarf 0.5 (judgement).

- [ ] spec field, inheritance, validation
- [ ] used by the plague code; a test that 0.5 halves a pulse
- [ ] shown on the peoples tab beside the life history

## Updates
- 2026-10-31: Created from inbox draft draft-disease-resistance-per-people.md (found by lane-85).
