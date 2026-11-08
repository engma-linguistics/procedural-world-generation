---
title: A whole radiation (the mammal stem's daughters) arises on one mid-sized continent; decide whether splits should spread by area within a radiation
type: task
status: needs-decision
parent: null
milestone: v5
subsystem: peoples
effort: m
impact: med
found_by: lane228
blocked_by: []
relates: [PW-888, PW-1184]
refs: [planet/lineages/history/origins.py::_origin_split, planet/lineages/history/origins.py::_by_landmass, planet/lineages/history/params.py::SPECIES_AREA_Z, tools/peoples_robust.py, docs/review/peoples/origins-spread.md, "world 4360a3 (time zoom cdc275)", "world af2677 (time zoom f2201f)"]
---

## In plain words
Each root line (reptiles, mammals, birds...) now starts on a landmass of its own, drawn by area. But every later people that branches
off a root is founded where its parent lives, so the whole family stays where its root began. On world 4360a3 the mammals' root often
starts on the third continent (15.5% of the ice-free land), and then 11-15 of the 22-23 peoples begin there: more than half in 5 of
8 dnd seeds and in 2 of 5 Seven Meals tries. No landmass under 15% held most in any of the 34 tries, so the PW-888 bar passes on the
letter, but the 15.5% continent sits on the line, and the owner's wish (10-25) was that most peoples should not arise on one smaller
landmass.

## Description
Measured in lane 228 (docs/review/peoples/origins-spread.md): per run, the present landmass under each people's origin, against that
landmass's share of the ice-free land. On 4360a3 (landmasses 29%, 22.3%, 15.5%) the 15.5% one held 12, 12, 13, 15 and 12 of 23 (dnd seeds 1, 2, 4, 5,
13), 12/22 and 14/22 (Seven Meals jitters 1-2) of the origins; on af2677 the largest landmass (48.7%) holds most, which is as species-area would have it.
The cause is descent, not the landmass draw: split origins are scored inside or beside the parent's range (with a 3x weight on cut-off
parts of it), and the across-sea branch (0.6 x K x crossing reach) rarely wins. The owner ruled 10-27 that related peoples clustering
near their ancestor is fine before boats.
Options:
- A: leave it (the ruling of 10-27 covers it; the bar holds).
- B: give a split's across-sea founders more weight in proportion to the far landmass's habitable area (the same area^z rule the roots
  use), so a large radiation leaks onto the big continents over Myr. Needs a sourced rate for over-sea founder events between
  continents; to be found and read, not cited from memory.
- C: an in-situ speciation area threshold (the island-radiation literature has one; to be sourced): a landmass too small for a
  radiation hosts daughters by founders from elsewhere only.
Lean: A for v5; B if the owner sees one continent hosting most peoples in the viewer.
