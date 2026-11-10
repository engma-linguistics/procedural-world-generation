---
title: The 1 Mkm2 floor (D71) - decide whether it applies when a people is founded (measured: it does not pay for itself)
type: task
status: needs-decision
parent: null
milestone: v5
subsystem: peoples
effort: s
impact: high
found_by: lane269c
blocked_by: []
relates: [PW-1558, PW-1182]
refs: ["planet/lineages/history/origins.py::_founders_room", "planet/lineages/history/origins.py::_origin_split", "planet/lineages/history/dispersal.py::_refuge_cell", docs/review/peoples/origins-spread.md, "tests/test_lineages.py::test_demography_defaults_inheritance_and_numbers", "side branch lane269d-armA (1d6a4c39, not for merge)"]
---
## In plain words
You ruled that no land people should finish a history under 1 million km2. A few small peoples still do. They are not being
pushed out. They are born on a small patch of country that suits them (a cold highland on a tropical continent, say) and they
fill it, and the patch is under 1 million km2. We could make "born only where there is room for 1 million km2" a rule of the
model. We measured that rule on the full robustness suite. It fixes goliaths but not bugbears or kobolds, it changes every Seven
Meals run, and it overall gains one run over simply leaving the model as committed. So the lean is not to add the rule, and
instead to lower the bar to 0.5 million km2, which the committed model already meets in every dnd run.

## Description
Baseline throughout: main fdb11199. Suite: world af2677, 17 dnd and 5 Seven Meals runs. "Committed" = branch lane269b at 32e9fb19
(a split's habitat patch must hold one founders' country, about 0.5 Mkm2). "Floor at founding" = that plus side branch
lane269d-armA (1d6a4c39): the patch must hold 1 Mkm2, else the people arises at the nearest free country that does.

Land peoples under 1 Mkm2 at the end, dnd (drow and troglodytes apart): main 29 people-runs; committed 9; floor at founding 8.
- Committed: bugbear 3 (0.50), goliath 5 (0.55-0.83), kobold 1 (0.50).
- Floor at founding: goliath 0, bugbear 3 (lower, 0.37), kobold 1 (0.98), aarakocra 4 (0.95 and three at 1.00 rounded).
- Seven Meals, under 1: main 7, committed 7, floor at founding 6 (dwarf in 4 runs, goliath 1, half_orc never founded).
- Fragile peoples (report "BRITTLE", worst swing between neighbouring runs): dnd main 7 (worst 2,170x hobgoblin), committed 4 (52x
  drow), floor 4 (77x drow). Seven Meals main 6 (1,020x half_orc), committed 6 (1,090x), floor 5 (1,200x).
- Seven Meals runs that differ from main: committed 2 of 5 (j1, j2); floor at founding 5 of 5. Dwarf there goes from 1 run
  under 1 to 4, dragonborn's smallest falls from 8.2 to 2.7 Mkm2.
- Farthest a founder or refuge moves: main 5,592 km (refuge); committed 7,251 km; floor 6,930 km (limit 8,000).

Options:
- (A) The floor applies at founding. Runs under 1: 8 (dnd). Fragile: 4 / 5. Seven Meals: all 5 runs change, dwarf worse. Farthest
  move 6,930 km. Test: still fails (below). Cures goliath only.
- (B) Keep as committed; list goliath, bugbear and kobold next to drow and troglodytes as known exceptions. Runs under 1: 9
  (dnd). Fragile: 4 / 6. Seven Meals: 2 of 5 change. Farthest 7,251 km. Test: fails (below).
- (C) Lower the bar to 0.5 Mkm2 (the model's own refuge floor) on top of (B). Runs under 0.5 in dnd: 0 (lowest bugbear and kobold
  0.50, goliath 0.55). Fragile and Seven Meals as (B). Same farthest and test. Needs your yes on the number.

## The test
`tests/test_lineages.py::test_demography_defaults_inheritance_and_numbers` asserts `f.population > 100 x g2.population`. On main
the second people (g2) is stranded on a fake island, so f is vastly bigger. With the fix g2 is founded off the island and grows
(f 4,821,793 against 100 x 889,509), so the test fails. It fails identically under the floor at founding (A) and under B and C
(same numbers). It is not a regression; the assertion encodes the stranding. Changing the assertion is part of this decision,
and the not-slow suite is otherwise green (1 failed, 1975 passed on the committed branch).

## Lean
C. The floor at founding fixes one people (goliath) at the price of changing all of Seven Meals and making its dwarf fragile, and
gains one run over B. The committed model already keeps every dnd land people at or above 0.50 Mkm2, so lowering the bar to
0.5 asks for no new mechanism. If you prefer to keep 1, take B with the exceptions listed.
