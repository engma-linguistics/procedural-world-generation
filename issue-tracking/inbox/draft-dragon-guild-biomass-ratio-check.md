---
title: "Food budget: the dragons alone reach a whole modern predator guild's prey:predator biomass (127:1), and the guild with them comes to ~46:1; check against a living guild"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: dragon-density-doc
blocked_by: []
relates: [PW-977, PW-990, PW-1019]
refs: [planet/lineages/history/megafauna.py, planet/lineages/dragon_ages.py, docs/review/megafauna/dragon-density/claims.md]
---

## Description
**In plain words.** The model's dragons are cheap to feed, because they burn energy like reptiles. So even though they get only a sixth of the food, their weight per km² is as high as a whole pack of modern mammal hunters put together. Is that what we want?

Numbers (docs/review/megafauna/dragon-density/numbers.json): where nobody else eats, prey:dragon biomass is 127:1 counting every age at
the mean mass 1.26 t (96:1 at the 1.65 t ecological mass). Farlow 1993 (p. 176) gives 200:1 to 100:1 for modern large-mammal
communities, as low as 45:1. If the smaller predators' biomass follows Carbone, Turvey & Bielby 2011's classes (Table 1, p. 2683:
individuals x mass, 1.8 times the apex classes' biomass), the whole guild comes to ~46:1 (claims.md C23). Farlow's ectotherm case
(p. 187) finds a predator as large as its prey feasible at 10:1, so a reptile-rate guild can be that dense.

Options:
- **A.** Keep: dragons are reptile-rate eaters, and a dense guild follows (no change).
- **B.** Check the guild split against a living guild (PW-1019's Serengeti item) and adjust `guild_ratio` only if a sourced figure disagrees.
- **C.** Split the guild by biomass rather than by food (a different reading of Carbone 2011's table).

Lean: A now, B as part of PW-1019. C is a reading change without a source.
