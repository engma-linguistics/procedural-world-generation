---
title: Exonyms - the folk-category table and how long a conquest is remembered need the owner (no conquest survives the default decay in run 45157b)
type: task
status: needs-decision
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun12
blocked_by: []
relates: [PW-731, PW-734, PW-661]
refs: [planet/lineages/reputation.py, planet/lineages/samples/dnd.toml, "run 45157b", docs/review/lineages/briefs/SCHEMA.md]
---

## Description
PW-731 v0 is built (`reputation.py`, `[[exonym]]` rows, brief_version 5). On run 45157b (fantasy, world 1df1c3) the reputation table has
144 exotic, 82 neighbour, 24 edge rows and NO feared/despised ones: the substrate takeovers in the run are all 1.5-80 kyr old (median
about 12 kyr), and a conquest fades with e-folding 1.5 kyr x the era scale (1.6 for renaissance) = 2.4 kyr, so they are under the 5% floor.
Options for the owner's "devils from the steppe" story:
- A: per-row `efold_kyr` (already supported): the devil/demon rows get a long memory (20+ kyr), a legend that outlives the event. Lean: A.
- B: lengthen the global decay (meta.reputation.efold_kyr), which also keeps every ordinary conquest.
- C: a legend floor: once a category row has been earned, the name stays at low strength regardless of age.
Also owner's: the generic table in dnd.toml (devil = horns, demon = antlers, giant-kin by ancestry, sea elves = swimmer descended from elves,
fae = arrivals, goblin menace) and the rich/thin thresholds (20000 / 3000 years in contact; the run's contacts span 100s of kyr, so most pairs read "rich" or "exotic").
Not read yet: authored conquests and polities, derived incursions (PW-661): no "resented" (ruled by) valence.
- [ ] with the PW-734 answers, rows that make humans next to the antelope/cervid folk call them devils (conquest basis) and humans among the cervid folk use an ordinary name.
