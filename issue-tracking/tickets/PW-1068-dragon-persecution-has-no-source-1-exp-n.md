---
id: PW-1068
title: "Dragon persecution has no source: 1 - exp(-N/0.05) presses every dragon to 1 per 5,000 km2 at any settled density"
type: task
status: in-progress
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977, PW-1001, PW-961]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/index.html, docs/references/wishlist.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** Wherever people live, the model pushes dragons almost to nothing, and the rule that does it was set by hand. A
band of foragers at one person per 10 km2 already does 86% of the pushing (on a log scale); any settled people does all of it. In the
review's paired runs the pressure takes peopled country down to 0.7% to 3% of its pressure-off density (medians), almost all through
persecution. No paper consulted supports it.

Evidence (review round 2, sections 5.2, 8, 9.2 item 1):
- persecution alone divides density by 92 in farmers' and 26 in foragers' country; overkill a further 1.6 in farmers' (third arm, roll 7000; Table 3);
- Ripple et al. 2014 measure range, not density: the 17 of 31 largest carnivores with estimates hold on average 47% of their
  historical ranges (p. 1241484-1); tolerance differs by species (pumas vs gray wolves, p. 1241484-6);
- Hamilton et al. 2007's forager densities 0.03-0.09 people/km2 (Table 1, p. 4767) already give a pressure of 0.45-0.83;
- two candidate sources are on the wishlist, not read: Cardillo et al. 2004, Woodroffe 2000.

Direction and size: more dragons in peopled country, up to the pressure-off arm (x120 farmers', x140 foragers', medians over 24 pairs).
Options:
- **A.** Persecution as a kill rate against the dragons' slow breeding (equilibrium natural x (1 - kill / r_max)), the kill rising with
  the peoples' numbers and means (PW-961), never species-ending (owner, 10-29); retire the 1 per 5,000 km2 floor.
- **B.** Keep the form, soften PRESS_N0 by a sourced amount once Cardillo/Woodroffe are read.
Lean: A (it is PW-977 stage 3); read the two wishlist papers first.
- [ ] fetch Cardillo 2004, Woodroffe 2000
- [ ] decide A/B

## Updates
- 2026-10-30: Owner 10-30 D14: make dragon pressure a setting or set of settings (e.g. per tech era). D16: wants dragons to press back on peoples (predation on small folk keeps game plentiful); later, metallics coexist more and chromatics stay combative.
- 2026-10-30: Status needs-decision -> in-progress. Owner 10-30: start immediately (it may rewrite the dragon paper). Lane 63.
- 2026-10-30: Owner 10-30: losing ~99% of dragons in farmland is too fatal for low-tech peoples. Early peoples' pressure should be very slight everywhere, rising with tech and history. Pressure must come from a source that scales with tech (weapons, organised hunts, settlement), not a flat per-capita kill rate. Next fun lane after 61.
- 2026-10-30: Created from inbox draft draft-dragon-pressure-source.md (found by dragon-density-r2).
