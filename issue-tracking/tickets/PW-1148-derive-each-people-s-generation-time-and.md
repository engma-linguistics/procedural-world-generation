---
id: PW-1148
title: Derive each people's generation time and growth rate from canon ages and a breeding class
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: highlights
effort: m
impact: med
found_by: lane76
blocked_by: []
relates: [PW-917, PW-888, PW-937]
refs: [planet/lineages/spec.py, planet/lineages/samples/dnd.toml, planet/lineages/history/peoples.py, planet/lineages/history/dispersal.py, planet/lineages/history/origins.py]
created: 2026-10-30
updated: 2026-10-30
---

## In plain words
Each people's "years per generation" is typed in by hand today, and several values disagree with D&D's own ages. Elves come out
nearer 200 years than 50. Hobgoblins and bugbears inherit the goblins' 15 even though canon makes them human-like. Instead, the
tree should hold the canon ages (age of adulthood, lifespan) and a breeding class, and work out the generation time and the
growth rate from those.

## Description
Lane 76 (peoples demography research, findings in its report) built a simple life table:
- human forager anchor: first birth 19.5 yr and interbirth interval 3.69 yr (Robson & Wood 2008 Table 2); 57% survive to 15 and
  64% of 15-year-olds reach 45 (Gurven & Kaplan 2007 p. 326);
- adult mortality is the human hazard, stretched to the canon lifespan; the fertile window is stretched the same way;
- T is the mean age of mothers;
- r_max = ln(Rmax) / T, with Rmax ~3.5 per generation for mammals (Ginzburg, Burger & Damuth 2010).

Results: T is ~29 humans, 18 orcs and kobolds, 15 goblins, 41 halflings, 110 dwarves and gnomes, ~200 elves (100 with a
shorter fertile window). r relative to humans: elves 0.14, dwarves 0.26, halflings 0.7, orcs 1.6, goblins and kobolds ~1.6–3.

- [ ] spec fields `adult_yr`, `lifespan_yr`, `breeding` (slow | mammal | brood: Rmax 2 / 3.5 / 7), optional `fertile_yr` [from, to]; inherited like `generation_yr`
- [ ] `gen_yr` returns the derived T (dragons keep `dragon_ages`); a hand `generation_yr` still overrides
- [ ] dnd.toml filled from the canon table (sources: dnd5e.wikidot.com lineage pages, listed in lane 76's findings)
- [ ] r_max exposed per line in the run output and workbench (no model use yet: the next draft)
- [ ] golden and lineages tests updated (viability numbers shift: elves' line_mvp falls from 1/2 to ~1/8 of the tree's)

## Updates
- 2026-10-30: Created from inbox draft draft-life-history-from-canon-ages.md (found by lane76).
