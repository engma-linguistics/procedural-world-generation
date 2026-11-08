---
id: PW-1184
title: A split whose stem has died out, or has no room nearby, is founded at the best habitat anywhere in the world
type: task
status: todo
parent: null
milestone: v5
subsystem: peoples
effort: s
impact: high
found_by: lane77
blocked_by: [PW-1558]
relates: [PW-1151, PW-1152, PW-677]
refs: [planet/lineages/history/origins.py, planet/lineages/history/dispersal.py, tools/peoples_robust.py]
created: 2026-10-30
updated: 2026-11-08
---

## In plain words
A new people should branch off where its parent people lives. In about one run in five, the parent stem has already died out or
been pushed out before the split date. The new people is then simply placed at the best spot for it anywhere on the planet, which
can be another continent. The same happens when the parent has no suitable country nearby. Where a people starts then depends on
whether its stem happened to survive, which changes from seed to seed. Leonins, goblins and halflings are hit the most, and the
troglodytes in nearly every run.

## Description
origins._origin_split falls back to _origin_fallback (argmax of K x noise over the whole grid) in two cases:
- "parent gone": the parent has no presence. Across the lane 77 suite (~90 runs per people): troglodyte 57/62 runs, leonin 23/82, goblin
  14/90, halfling 10/86, dwarf 3, orc 2, goliath 2, firbolg 2, tabaxi 1. Two causes, both general:
  1. Same-date siblings: the troglodytes and lizardfolk both split at 2.5 Myr. Once the lizardfolk start, every *living* child has
     started (tree.living_children leaves out a child set to die out), so _start_due ends the stem before the troglodytes found.
     _start_due should end a stem only after all its children due at this step have started, including the ones authored to die out.
  2. A stem that holds nothing by its later splits: the feline stem by the leonin (900 kyr), the goblinoid stem by the goblins
     (400 kyr), the archaic humans by the halflings (100 kyr; their daughter, the humans, live in the same country). The suite records
     only that the parent held no cells at the split; why each stem went (outcompeted, faded, no habitat) is still to check.
     _hold_out keeps a refuge only for lines living at the present (tree.leaves()). A stem with children still to come is just as
     much "given as living" until its last split.
- "no room for it by the parent: best habitat": no cell within 4 rings of the parent's range has K > 2 EST: orc 21/82, dwarf 20/86,
  bugbear 12/82, elf, gnome, centaur.
Fix (general, small): (1) end a stem only once all its children due by this step have started; (2) _hold_out counts a stem with
unstarted children as living; (3) the "no room" fallback founds at the best habitat weighted by distance from the parent's range
(the across-sea weighting already in _origin_split), not at the world's best cell. With SPLIT_FOUNDING = local (PW-1152), this keeps
"one spot, near the parent" true for every split.
- [ ] fallback counts in the suite's origins ("why") drop to ~0 for parent-gone; the brittle peoples' swing (leonin, goblin, halfling) narrows

## Updates
- 2026-11-08: Lane 228 (d01c4a08): the three asked-for fixes were already on main (4a01368b); added _take (a daughter taking the stem's last land saves it as the stem's last land) and relabelled the Seven Meals merfolk founding. Parent-gone fallbacks 2 -> 0. Swing on the dnd jitters unchanged; blocked by PW-1558 (stem refuge teleport).
- 2026-11-03: Milestones 11-03: v2 -> v5: v5 must-have: splits founded near their parents in Seven Meals
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-split-teleports-when-stem-gone.md (found by lane77).
