---
id: PW-1312
title: "Food taboos should reach the culinary book: a per-culture forbidden-foods list in the brief, and taboos reading the real culinary data (staples, seafood, game)"
type: task
status: in-progress
parent: PW-1308
milestone: v2
subsystem: food
effort: m
impact: med
found_by: lane117
blocked_by: []
relates: [PW-1305, PW-692, PW-719, PW-1306]
refs: ["planet/lineages/taboos.py::culture_taboos", "planet/lineages/taboos.py::ITEMS", "planet/lineages/brief.py::_cultures", "planet/lineages/brief.py::_animal_foods", planet/lineages/animal_defs.py, planet/lineages/crop_defs.py, planet/lineages/seafood.py, planet/lineages/prey.py, "brief.py NOT_MEAT dog (canid taboo, PW-719)", docs/review/religion/slice1.md, "run b4d502"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: slice 1 writes `taboos.json` and lists each culture's taboos in the brief's cultures section, but the brief's food goods (`_animal_foods`, the
meat and dairy lists) do not yet drop a forbidden food, and the taboo targets come from a small fixed table of wild kinds plus the run's seven domesticates and its
crops, not from what a culture's land actually offers (seafood.py fish and shellfish runs, prey.py game, megafauna).

- [ ] Make the brief's `_animal_foods` and crop lists carry a per-culture `forbidden` set (scope everyone vs priests vs a lineage), so the culinary book can say "the X do not eat Y".
- [ ] Replace `taboos.ITEMS` availability (coastal trait, wet country) with the culture's real fisheries/game from the run's layers, and let `divine` and `purity` pick from them.
- [ ] Connect the dog: brief.py `NOT_MEAT = ("dog",)` is a blanket canid taboo (PW-719); make it a culture's taboo (purity, `DOMESTIC_STRADDLE["dog"]`) instead.
- [ ] Source the straddle table (Douglas 1966) from a read copy; today it is my reading of the scheme, marked JUDGEMENT.

## Updates
- 2026-11-03: Lane 167: points 2-4 left. 2 needs the per-culture land sampled against the seafood and prey layers inside taboos.derive, which today reads no layers (not small); 3 changes whether the culinary book says dogs are eaten, a content call for Daniel; 4 needs a read copy of Douglas 1966, none is held. Also: the brief and cuisine sheet now read the Religion tab's docs (PW-1440).
- 2026-11-03: Status todo -> in-progress. Lane 164: point 1 done in the cuisine sheet: a culture's food taboos (scope everyone) drop out of its staple, herd and dairy lists, and the sheet lists what it won't eat, split into its faith's and its own (cuisine.py::profile, wont_eat). Points 2-4 (real fisheries and game as targets, the dog as a culture taboo, Douglas 1966 from a read copy) remain. docs/review/food/cuisine-sheet/round1.md
- 2026-11-02: Created from inbox draft draft-taboos-feed-culinary-diet.md (found by lane117).
