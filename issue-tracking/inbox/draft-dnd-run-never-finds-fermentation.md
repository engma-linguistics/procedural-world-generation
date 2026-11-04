---
title: "D&D run a2b637: no people ever finds fermentation, so every D&D cuisine sheet says 'no beer or wine yet'"
type: task
status: todo
parent: PW-856
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lane164
blocked_by: []
relates: [PW-1141, PW-1391, PW-744]
refs: ["planet/lineages/samples/techtree.toml (id fermentation: needs cooking, containers; earliest 13 kyr; rate 0.02)", "planet/lineages/cuisine.py::drink", "run a2b637 (meta.techtree.known)", "run 3c1caf (Seven Meals: humans know fermentation 10.2 kyr ago)", docs/review/food/cuisine-sheet/round1.md]
---

## Description
In plain words: in the newest D&D peoples run (a2b637, the only D&D run that parses with today's code) no people knows fermentation at
the present, although every people has had its two prerequisites (cooking, containers) for over 40 kyr. The Seven Meals run 3c1caf
has it from ~10 kyr ago. The cuisine sheet (PW-1391) gates beer and wine on fermentation, so every D&D culture, cities included, reads
"no beer or wine yet (the people does not know fermentation)". What breaks if never done: the culinary book's Drink line is wrong for the
whole D&D preset, and a reader will trust it.

Check first whether this is one unlucky draw or systematic for the D&D tree (re-run or read two or three more D&D runs once they exist on
current code); PW-1141 says single-origin Pleistocene techs come late, and here it never comes at all.
- [ ] fermentation known by most farming peoples at the present on two or three D&D runs, or a stated reason why not
