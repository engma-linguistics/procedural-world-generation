---
id: PW-1756
title: "Wild fauna catalogue: ~20-30 wild animals (deer, wolf, bear, big cats, bison, mammoth-type megafauna, boar, beaver...) with ranges through time, read-only beside the 13 herd animals"
type: task
status: todo
parent: null
milestone: v1.0
subsystem: peoples
effort: l
impact: med
found_by: owner
blocked_by: []
relates: [PW-719, PW-691, PW-207, PW-1745]
refs: [planet/lineages/animal_defs.py, planet/lineages/animals.py, planet/lineages/kitchen_time.py, viewer/lineages.html]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** Daniel (11-11) would like more granular flora and fauna, for example "to find historic ranges of certain animals". Today the history tracks 13 animals (horse, dog, wild sheep and goats, cattle, fowl, pig, reindeer, camel, llama, buffalo, yak, great elk, riding lizard). Each has a habitat rule and a wild-range layer stored on every frame (`animal_wild`), so their past ranges already exist. Add a wider set of wild animals people hunt, fear or name, using the same pattern: a habitat rule from the frame's climate, vegetation and ice, plus extinction or retreat rules where hunting or ice ages drive them (e.g. mammoth-type megafauna gone where hunters spread). Show "where did X live at time T" in the viewer.

**Scope guard.** The new animals are READ-ONLY layers: they don't feed density, herds or dragons, so they can't change a history's people, states or numbers. A run's history must be byte-identical with and without them, apart from the new layers. Storage: a second bit-flag layer (uint32) per frame.

**Done when:** about 20-30 animals each have a sourced habitat rule; the per-frame wild-range layer is stored; the viewer shows an animal's range at the chosen time; there are tests, including the byte-identity check; and it's sanity-checked by eye on Earth-like runs. A flora counterpart (named wild plants beyond the crop wild ranges) is a separate follow-up.

## Updates
- 2026-11-11: Created from inbox draft draft-wild-fauna-ranges.md (found by owner).
