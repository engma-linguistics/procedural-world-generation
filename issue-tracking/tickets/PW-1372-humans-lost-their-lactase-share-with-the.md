---
id: PW-1372
title: "Humans lost their lactase share with the herder groups (PW-1357): derive it from the herding the ladder finds"
type: task
status: done
parent: null
milestone: v2
subsystem: food
effort: s
impact: low
found_by: lane 136 / lane 137 (density ladder build)
blocked_by: []
relates: [PW-1357, PW-1275, PW-784, PW-723]
refs: ["planet/lineages/animals.py::Animals.summary (dairy, PW-784)", "planet/lineages/ladder.py::Ladder.line (herd share per cell)", "planet/lineages/ladder.py::Ladder.sh", planet/lineages/samples/dnd.toml, "git show 5849cae3:planet/lineages/samples/dnd.toml (lines 643, 751, 766: milk 0.1 steppe_orc, 0.6 the human herder groups)", planet/lineages/brief.py, docs/review/peoples/density-ladder/build.md]
created: 2026-11-02
updated: 2026-11-03
---

## Description
Before PW-1357 the D&D preset's human herder groups carried `body = { milk = 0.6 }` (lactase persistence in herding peoples) and the
steppe orcs `milk = 0.1`. The groups are gone (peoples have no groups; ways of life come from the density ladder), so humans now have
no lactase share at all, and the dairy summary (`animals.Animals.summary`) reads only the static `[[use]]` herd share for `milks`.
Humans who herd on the ladder (the nomad and agro-pastoral rungs: about a tenth of humans in the lane 137 dnd runs) therefore drink
no fresh milk.

What to try: derive a people's lactase share from its realized herding over time (the ladder's per-cell herd share, people weighted,
since herding was taken up) instead of an authored number; or, simpler, author `milk` on the human people itself. Lactase stays a
population frequency (a share, PW-723).

## Updates
- 2026-11-03: Status todo -> done. Lane 164: a culture's lactase share = max(authored body.milk, herd share x min(1, years since milking was known / 5 kyr)) in cuisine.py::dairy_of (LACTASE_KYR, a JUDGEMENT placeholder shape, not a fitted selection rate); fresh milk at >= 0.6. Herding humans get fresh milk again after long dairying, without an authored number.
- 2026-11-02: Created from inbox draft draft-human-lactase-without-herder-groups.md (found by lane 136 / lane 137 (density ladder build)).
