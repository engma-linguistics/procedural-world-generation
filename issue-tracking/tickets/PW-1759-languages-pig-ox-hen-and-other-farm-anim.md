---
id: PW-1759
title: "Languages: core-list farm-animal words (PIG, OX, HEN) stay native where the world never tamed the animal; matrix needs a current-code peoples run"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: xs
impact: low
found_by: lang-lane20
blocked_by: []
relates: [PW-1745]
refs: ["planet/language/lexicon.py::_all_concepts", planet/language/history.py, planet/lineages/animal_defs.py, planet/lineages/animals.py, docs/review/language/for-daniel.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: lane 20 (PW-1745) gates animal words by wild range and herd spread for the animals the run stocks (meta.animals.stocks). Core-list words for farm animals the run does not stock (PIG, OX, HEN and the like, which come from the Concepticon lists, not animal_defs) stay proto words everywhere, so a world with no pigs still has a native 'pig' in every language. Gate them like wild fauna (by a wild-range proxy from animal_defs where one exists), or drop them from lexicons when the run lacks the animal.
- [ ] no lect has a native word for a farm animal its world never had

## Updates
- 2026-11-11: Created.
- 2026-11-11: Correction (11-11): pigs and chickens do exist in the model. Chickens are the 'fowl' stock, present in every world. Pigs, reindeer, camel, llama, buffalo and yak were added on 11-09 (2c9e96fa, PW-835), but every peoples run on disk predates that (a24559, de1cc6, 0141d1, 3e0eb4, 1e97dd, 216848, 07c755, 3c1caf, a2b637 all stock only horse, dog, caprine, cattle and fowl). A world made with current code stocks pigs wherever a people tames them. This ticket therefore matters for (a) old runs and (b) a world where an animal is never tamed. Main action: the language matrix (PW-1737) should include a peoples run made with current code, so PW-1745's gating of the newer herd animals gets exercised.
