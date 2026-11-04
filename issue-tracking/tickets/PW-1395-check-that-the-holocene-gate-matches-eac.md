---
id: PW-1395
title: Check that the Holocene gate matches each world's own last deglaciation (gate_kyr 11.6, HOLOCENE_KYR)
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-832, PW-1125]
refs: ["docs/review/fresh-eyes/2026-11-03.md#2-recommendations-ranked", planet/lineages/samples/techtree.toml, "planet/lineages/history/params.py::HOLOCENE_KYR", planet/finish.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: the peoples' calendar assumes Earth's Holocene: the tech tree's hard gate is `gate_kyr = 11.6` (samples/techtree.toml:40) and `HOLOCENE_KYR = 10` (history/params.py:69), but a world's "now" is the latest interglacial's sea-level peak (finish.py:86-89, the review's citation), which can fall at another time on another planet. This ticket is the check only: on the showcase time zooms, read when each world's last deglaciation actually ended and compare it with 11.6 and 10.
- [ ] a short table: world, own last-deglaciation age, gate_kyr, HOLOCENE_KYR
- [ ] if they differ by more than a few kyr, say so on PW-832 / PW-1125 (which already ask to key the gate to the world's own deglaciation) and fold the fix there; no change here
Planet-relative, not Earth numbers (owner ruling on planet-relative thresholds).

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-11-03: Created.
