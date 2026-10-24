---
id: PW-691
title: "Domestication: animals and plants peoples tame, from wild ranges to herds and crops, with rare non-Earth options"
type: epic
status: in-progress
parent: null
milestone: v2
subsystem: timezoom
effort: xl
impact: high
found_by: daniel
blocked_by: []
relates: [PW-688, PW-103, PW-675]
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24), with horses (PW-688): nomads and herders need something to herd. Wild ranges derived from the land (no fauna is simulated, PW-184): grazers of steppe and grassland (horse-, cattle-, sheep-, goat-, camel-, reindeer-, llama-like), fowl, dogs; and crops from the vegetation (grains, tubers, rice-like, fruit trees). Each has a homeland and date of taming (Earth anchors: dog ~15+ kyr, sheep/goat ~11 kyr, cattle ~10.5 kyr, horse ~5.5 kyr) and spreads with the peoples who take it up, setting what herders herd and farmers grow. Optionally, as a rare possibility, domestications Earth never made (zebra-, elk-, giant-bird-, lizard-mount-like, fantasy beasts), off by default, forceable for tests. Feeds land use (PW-662), transport (PW-688) and the culinary ethnography goal.

## Updates
- 2026-10-23: Status todo -> in-progress. Animals merged (dog, sheep/goat, cattle, fowl, horse; Animal table). Plants (crops) next.
- 2026-10-24: Animals built on branch fun6: one `Animal` table, bit-flag layers animal_wild / animal_known, dog, sheep and goat, cattle (dairy, plough), fowl, two rare fantasy rows; see docs/proposals/lineages.md 'Animals (PW-691) and boats'. Plants, camels/reindeer/llamas, separate stocks and per-cell goods for PW-692 remain (drafts).
- 2026-10-23: Horses built as the first animal (see PW-688). A short design note for dog, sheep and goat, cattle and fowl is in docs/proposals/lineages.md ('Next animals'); the shared step is to move the horse constants into an animal table. Not built.
- 2026-10-23: Owner (2026-10-24): wild ranges from the land by biome (jungle for junglefowl, grassland for horses and cattle; eland-like and other African-style fauna where their biome is, mostly not for taming). Horses first; if that and its tests and runs work, add the rest as many at a time as fits. A first pass may let a species be tamed more than once and treat the results as one homogeneous stock ('just horses'); tracking separate stocks (e.g. continent-3 goblin dogs vs continent-2 human dogs) waits for the epic proper.
- 2026-10-23: Created.
