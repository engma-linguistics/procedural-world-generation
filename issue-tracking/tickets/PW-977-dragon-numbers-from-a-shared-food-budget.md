---
id: PW-977
title: Dragon numbers from a shared food budget - the land's surplus split between dragons, hunters and herders, not a fixed 1 per 5,000 km2
type: story
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: l
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-958, PW-957, PW-960, PW-961, PW-973, PW-974, PW-975, PW-833]
refs: [planet/lineages/history/megafauna.py, planet/lineages/prey.py, docs/review/megafauna/age-of-dragons.html]
created: 2026-10-28
updated: 2026-10-29
---

## Description
Owner 10-28, on the PW-967 review: the natural numbers are frightening, and 1 per 5,000 km2 is an assumption that peoples kill
dragons down. Is there a "homeostasis" number from the prey, the land and the peoples sharing it, especially before
civilisation, when peoples can't kill dragons and live alongside them in uneasy truces and pay tribute?

The review's section 5 shows the problem. With the present 1 per 5,000 km2 fixed, an ancient eats 106-270% a year of the herders'
stock in its range. That is not a steady state: the herders leave, or the dragon eats wild prey, moves or starves. The present
number should come out of food, not go in as a setting.

Proposal: make the present density an equilibrium of one budget per region.
- Supply. Wild herbivore production from NPP (prey.py, McNaughton 1989 slope via PW-975), times a sustainable offtake (~10%/yr,
  the review's figure, to source). Herders' stock adds to it, with a tolerable loss share before herders abandon a range (to
  source). Farmers' fields add nothing directly.
- Demand. Each people's hunters take their share (density x way of life, PW-833/PW-974). Other big predators take theirs: the
  dragons are not the whole guild (Carbone, Turvey & Bielby 2011 on intra-guild competition is on file). Dragons get the rest.
- Dragon density = dragons' share / food per dragon (from the PW-958 age schedule's mass and cattle a year).
- Persecution (PW-973 option C) is a separate, explicit factor: zero for foragers who can't kill dragons, rising with peoples'
  reach, iron, organised bounties (PW-961). meta.dragon_km2 becomes a floor or retires.
- Tribute falls out: a valley's stock loss the herders accept rather than leave is the tribute.

This makes the pre-farming world sit near "dragons eat most of the surplus, foragers live in the gaps", and lets dragons decline
as herders, farmers and weapons spread, a path rather than a fixed end state.

Options:
- **A.** Build the budget (above). Large; depends on PW-974 (people density from productivity) and PW-975.
- **B.** Keep the fixed present density, cap the livestock share in section 5 so no dragon eats over ~X% of its range's stock
  (a clamp).
- **C.** A, staged: first the dragons' food cap against wild prey plus stock (fixes the >100% cases), then the peoples' share,
  then persecution.

Lean: C (A in stages), with the younger age schedule (PW-958), which halves food per dragon.

## Updates
- 2026-10-29: Stage 1 merged 10-29 (fun lane 43): food cap per cell (10%/yr wild offtake + 10%/yr stock, unverified, PW-991). It never binds at defaults (PW-990): the natural density from prey is already food-limited, and the old >100% stock shares were a metric that charged an ancient's whole kill to the herders' stock. Worst stock share now 0.9%/yr. Stages 2-3 next.
- 2026-10-29: fun-lane-43 stage 1 done: dragons of all kinds in a cell are held together to the food there (megafauna.food_scale: 10%/yr of the wild herds + 10%/yr of the herders' stock, both unverified, over the schedule's 5.4 cattle a year per dragon); wild prey and stock are taken in proportion to supply. meta.dragon_km2 still sets the pressed density; the cap applies on top as a minimum. Result: the cap never binds at the defaults (identical counts with it off on 4 of 4 checked runs; worst cell 16% of its supply, worst pocket stock loss 0.9%/yr); the old section 5 >100% was an artefact of putting an ancient's whole kill on the stock. Review page rebuilt (docs/review/megafauna/probe.py, age-of-dragons.html on 2a7385 L7, roll 7000). Drafts: cap does not bind (needs-decision), constants unsourced.
- 2026-10-28: Stage 1 also re-runs the PW-967 review page (age_of_dragons.py; rebuild a probe that writes RUN.npz/SERIES.json, since lane 41's is gone) with the new prey and the younger schedule.
- 2026-10-28: Status needs-decision -> todo. Owner 10-28: go with C (staged): 1) food cap against wild prey + stock, 2) peoples' share, 3) persecution. Younger schedule (PW-958). Stage 1 starts after the PW-975 McNaughton lane merges.
- 2026-10-28: Created from inbox draft draft-megafauna-food-budget-equilibrium.md (found by coordinator).
