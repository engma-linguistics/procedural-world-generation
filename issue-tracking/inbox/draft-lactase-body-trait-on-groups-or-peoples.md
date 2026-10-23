---
title: Lactase persistence (and other culture-linked body traits) in the preset sit on herder groups; decide group-level vs people-level
type: task
status: needs-decision
parent: PW-694
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: horses-senses
blocked_by: []
relates: [PW-694, PW-692, PW-665]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/spec.py]
---

## Description
PW-694 gave every people a `body` table (planet/lineages/spec.py BODY_DEFAULT; inherited key by key from the first parent). In the D&D preset I set `milk = true` on the groups `human_herder`, `human_nomad` and `steppe_orc` (lactase persistence follows herding cultures on Earth) and left the human people itself at `milk = false`.
Options:
- A (as built): traits that track a way of life sit on the group. Rolled-up summaries of the people then say "humans do not digest milk" while the herder group does. A future cuisine pass has to look at the groups.
- B: put it on the people at a population share (a `milk` fraction 0..1 instead of a bool), set by how much of the people herds.
- C: keep bools, set `milk = true` on `human` itself.
Lean: A for now (nothing reads it yet), B when PW-692 starts, since lactase persistence is a share of a population (~35% of humans on Earth), not a switch.
