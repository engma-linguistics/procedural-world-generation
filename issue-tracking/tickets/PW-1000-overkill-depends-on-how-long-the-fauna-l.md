---
id: PW-1000
title: "Overkill depends on how long the fauna lived beside people (Sandom 2014: ~0.02 / 0.23 / 0.46 species lost), not one OVERKILL = 0.6 everywhere"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: papers-1029
blocked_by: []
relates: [PW-966, PW-975]
refs: [planet/lineages/prey.py, docs/references/megafauna/sandom2014_megafauna_extinctions_humans_procb.pdf]
created: 2026-10-29
updated: 2026-10-29
---

## Description
`prey.OVERKILL` = 0.6: where small folk press the land fully, the wild big herbivores fall to 40% of their potential. The value is cited as "after Sandom et al. 2014". That paper (Proc R Soc B 281:20133254) is now on file. It measures something different and points to a different form.

What it gives:
- **Measure.** The share of large-mammal species (>= 10 kg) lost per country between 132 and 1 kyr BP. It counts species, not biomass or density.
- **Main driver: hominin history.** Per-country loss by region (Fig. 3 box plot, p. 5, medians read off the figure):
  - about 0.02 where hominins evolved (Africa; at most 13%, p. 6);
  - about 0.23 where archaic hominins came first;
  - about 0.46 (quartiles about 0.34-0.55, up to 0.78 in Uruguay, p. 5) where modern humans were the first hominins (the Americas, Australia).
- **Fit.** Hominin history alone explains 64% of the variation; climate explains 20% (p. 6). Table 1 (p. 5) gives the SAR model.

How it differs from ours:
1. Ours is one loss for every people's country. Sandom's loss depends on whether the fauna co-evolved with the people. A lineage history knows when and where each people arrived (and the sapiens node, PW-971), so the model could reproduce this. For example, overkill could scale with how recently the land's first people arrived, low in the homeland and high in the last-settled continents.
2. Ours is a biomass loss, and Sandom's is a species loss. Losing ~46% of the large species likely removes more than 46% of the large biomass, because the largest go first. So 0.6 as a biomass loss in newly settled land is plausible, but not taken from the paper.

Options:
- **A.** Keep 0.6 flat and fix the citation to "a judgement; Sandom's species losses are 0.02-0.46 by region". The comments already say this.
- **B.** Make the overkill depend on the people's arrival history: about 0.1 in the homeland of the first people, rising to about 0.6 where they arrived late. This needs the arrival time per cell from the history and a review of the prey maps.
- **C.** B, with the biomass-against-species step made explicit (a size-selective loss).

Lean: A for v1/v2 tidiness and B as a v2 fun feature, because it gives the "Africa kept its giants" pattern for free. A value change needs a world run and the prey-map review.

## Updates
- 2026-10-29: Created from inbox draft draft-overkill-by-hominin-history.md (found by papers-1029).
