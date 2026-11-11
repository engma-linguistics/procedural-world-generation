---
id: PW-1745
title: "Languages: things a people met late arrive as loans: gate animals by range and herd spread, add wild fauna and flora by biome, kitchen and everyday-item words"
type: story
status: todo
parent: PW-1736
milestone: v4
subsystem: culture
effort: l
impact: high
found_by: owner
blocked_by: []
relates: [PW-1738, PW-692, PW-184]
refs: ["planet/language/lexicon.py::_all_concepts", "planet/language/lexicon.py::concepts", "planet/language/lexicon.py::TECH_CONCEPT", planet/lineages/animal_defs.py, planet/lineages/animals.py, planet/lineages/keeping.py, planet/language/history.py, planet/language/data/concepts.tsv, docs/review/language/assessment-2026-11-11.html, "run a24559"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: Daniel 11-11: expand the everyday vocabulary (food, everyday items, animals, plants) so that words for things a people met late arrive late, as loans: a people that first sees a horse a few centuries before the end should say it with a borrowed word, the way crops already work.
What exists (a24559): 969 concepts, about 750 of them from the Concepticon core lists. Crops are gated by arrival (crop:wheat in 274 of 621 living lects, carried along food_routes, 73% of crop words loans), and techtree concepts (BREAD, CHEESE, MONEY, OVEN ...) arrive with their tech (lexicon.TECH_CONCEPT). Animals are not gated: the 4 domestic animals the run stocks (animal:horse, cattle, caprine, fowl) are proto=True for every proto-language (lexicon._all_concepts), so all 621 living lects have a native-looking 'horse' from 20 kyr ago, whether their people ever met one. The peoples run already knows the answer: animal_defs.wild_* ranges per animal and the taming and spread of each herd (planet/lineages/animals.py, keeping.py).
Do:
- [ ] animals gated like crops: a proto gets a native word only if its homeland overlaps the animal's wild range (wild_*) or the animal is already kept there; otherwise the word arrives when the herd (or contact with herders) reaches the deme: borrowed from the donor, or coined (a compound 'big dog', 'nose-cow'; a calque 'river horse'), with the route in the etymology as for crops. Use all 13 animal_defs rows the run stocks, plus their meat words (beef/cow already handled by contact.doublet)
- [ ] wild fauna and flora by biome, as local concepts (no fauna is simulated, PW-184: derive from the land like wild_*): generic kinds, never Earth species (big cat, ape/monkey, crocodile-kind, big snake, seal, whale, camel-kind, elephant-kind, parrot, palm, bamboo, cactus, conifer, mangrove ...); a lect knows those of the biomes its deme lived in, and a people moving into a new biome takes them from the locals (substrate, the existing shift path) or coins them
- [ ] the food and kitchen gaps the 11-11 assessment listed: chop, peel, slice, slaughter, grind; spoon, ladle, plate, sieve, basket, jar; oil, spice, stew, broth, sauce, flour; meals by time of day; texture words (crisp, tender, sticky) - culinary core for PW-692; tie tool and dish words to techtree items where one exists (extend TECH_CONCEPT)
- [ ] everyday items with the tech tree: cart/wheel, plough, loom/cloth kinds, metal names (copper, bronze, iron), boat kinds, saddle - each arriving with its tech, so late tech brings loanwords (Wanderwörter)
- [ ] checks: share of 'late' concepts that are loans vs coinages (real: new things are mostly borrowed or calqued); no lect has a native word for an animal its line never met
- [ ] keep the pass inside ~12 min at 8 workers and languages.json growth modest (concepts x 1,183 lects); measure on the PW-1737 matrix
Pairs naturally with PW-1738 (core words borrowed too often): one lane can make borrowing go where it belongs, less in the core and more for new things.

## Updates
- 2026-11-11: Created.
