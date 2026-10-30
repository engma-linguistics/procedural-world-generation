---
title: "Dragon persecution has no source: 1 - exp(-N/0.05) presses every dragon to 1 per 5,000 km2 at any settled density"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977, PW-1001, PW-961]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/index.html, docs/references/wishlist.md]
---

## Description
**In plain words.** Wherever people live, the model pushes dragons almost to nothing, and the rule that does it was set by hand. A
band of foragers at one person per 10 km2 already does 86% of the pushing (on a log scale); any settled people does all of it. In the
review's paired runs this one rule takes peopled country from the food's dragons down to under 3% of them. No paper on file supports it.

Evidence (review round 2, sections 4.2, 7 item 1, 8):
- persecution alone divides density by ~100 in farmers' and foragers' country (third arm, roll 7000; Table 3);
- Ripple et al. 2014 measure range, not density: the 17 of 31 largest carnivores with estimates hold on average 47% of their
  historical ranges (p. 1241484-1); tolerance differs by species (pumas vs gray wolves, p. 1241484-6);
- Hamilton et al. 2007's forager densities 0.03-0.09 people/km2 (Table 1, p. 4767) already give a pressure of 0.45-0.83;
- two candidate sources are on the wishlist, not read: Cardillo et al. 2004, Woodroffe 2000.

Direction and size: more dragons in peopled country, up to the pressure-off arm (~x270 farmers', ~x190 foragers', medians).
Options:
- **A.** Persecution as a kill rate against the dragons' slow breeding (equilibrium natural x (1 - kill / r_max)), the kill rising with
  the peoples' numbers and means (PW-961), never species-ending (owner, 10-29); retire the 1 per 5,000 km2 floor.
- **B.** Keep the form, soften PRESS_N0 by a sourced amount once Cardillo/Woodroffe are read.
Lean: A (it is PW-977 stage 3); read the two wishlist papers first.
- [ ] fetch Cardillo 2004, Woodroffe 2000
- [ ] decide A/B
