---
id: PW-1666
title: A root founded into a world already held by older roots is crushed at once and lives only by the refuge
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: lane 277 (worktree-agent-a7c46b5a720cb2320)
blocked_by: []
relates: []
refs: [planet/lineages/history/dispersal.py, planet/lineages/history/competition.py, planet/lineages/samples/everyone.toml, docs/review/peoples/everyone-experiment.md]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words

In the lane 277 "everyone" tree there are eight roots. The mammal root starts at 10 Myr, after the reptile, amphibian, fish, insect, plant and
fungus roots have filled the world. The older roots squeeze it out on the very step it is born. On main it survives only because the refuge rule
drops it into a pocket ("mammalian stem hold out in a refuge", 10,000 kyr ago, run fe887b on world 4360a3). With the refuge switched off
(`--set HOLD_OUT_REFUGE=false EXTINCT_STEMS=true`) it dies 1 Myr later, and so does every mammal people under it: no humans, no dwarves, no
goblins, no giants. Only the cats and dogs survive, because they split off on the step before the root died.

## Description

A stem is the ancestor species. Deep-time competition treats it as one people in closed country (ALPHA_CLOSED 1.4: the larger excludes the
smaller), so a late root has no room anywhere. The dnd tree does not show this because it has only three roots (run a2b637 logs no refuge for
the mammals). It will show in any tree that adds roots, and an owner-made tree may do that.

**What breaks if never done:** in a tree with more roots, a whole branch of the tree starts from one refuge pocket. Where it starts, and so
where every people under it starts, is set by the refuge cell rather than by the habitat. If anyone ever turns the floors off, that branch is
lost.

**Options:** found a root at its best free room (as arrivals do, `_origin_new`'s arrival_room) rather than at its best habitat; or let deep-time
stems of different roots compete at most as `among` peoples (they are not one guild). This needs a judgement call; it is not a slam dunk.

## Updates
- 2026-11-10: Created from inbox draft draft-late-root-crushed-at-birth.md (found by lane 277 (worktree-agent-a7c46b5a720cb2320)).
