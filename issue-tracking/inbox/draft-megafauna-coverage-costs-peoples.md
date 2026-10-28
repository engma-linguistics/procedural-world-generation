---
title: Megafauna coverage fixes (PW-936) cost the main peoples remnants; giant counts run to thousands
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-38
blocked_by: []
relates: [PW-936, PW-924, PW-923, PW-937]
refs: [planet/lineages/history/megafauna.py, planet/lineages/history/dispersal.py, "worlds 2a7385 1df1c3 e71172 6909cb a12762 067778, dnd rolls 7000-7003"]
---

## Description
Fun lane 38 acceptance sweep, 6 planets x rolls 7000-7003, dnd, one try each (24 runs per arm). Main peoples = human elf dwarf
halfling gnome orc goblin.

| arm | remnants < 100 cells | >= 300-cell pass | megafauna kinds >= 0.5 of core country (2a7385 + 1df1c3) |
|---|---|---|---|
| main | 18 | 126/168 = 75% | 48/116 |
| main + PW-937 only | 18 | 127/168 = 76% | 49/116 |
| final (PW-936 metapop fade + giants at fliers' reach + PW-937) | 24 | 117/168 = 70% | 106/116 |

PW-937 is neutral for peoples. The megafauna changes buy the coverage target (every kind is in most of its country) but cost peoples:
orcs pass 24 -> 19 (1df1c3 orcs fall to 17 cells on 3 of 4 rolls, 2a7385/7003 to 5), elves 17 -> 13, gnomes 10 -> 8; new remnants
are halflings and goblins on 067778. The pass rate is right at the 70% bar. Likely the much larger giant ranges taking K or competing
with the peoples sharing their country (hill giants now 6k-20k individuals, frost 4.5k-13k, storm 8k-15k; dragons stay in the
tens to low thousands). This conflicts with "a few hundred of each kind": giants' density is their own demo density, not meta.dragon_km2.
No variant split the metapop fade from the giant reach, so which part costs orcs is not proven.
- [ ] owner: accept the trade, or cap giant density (e.g. giants also on a km2-per-individual option like dragons)
- [ ] probe which part (metapop fade vs giant reach) presses orcs on 1df1c3 and fix it at the cause

## Updates
- 2026-10-28: Created.
