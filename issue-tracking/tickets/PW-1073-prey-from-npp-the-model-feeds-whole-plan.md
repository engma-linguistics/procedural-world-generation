---
id: PW-1073
title: "Prey from NPP: the model feeds whole-plant herb NPP (roots in) to McNaughton et al.'s above-ground fit, and reads its whole-herbivore biomass (insects in) as big game"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: high
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977, PW-990]
refs: [planet/lineages/prey.py, planet/gameattrs.py, planet/vegetation.py, docs/review/megafauna/dragon-density/index.html, docs/review/megafauna/dragon-density/sensitivity.py]
created: 2026-10-30
updated: 2026-10-31
---

## Description
**In plain words.** The number of grazers the model puts on a piece of land comes from a published formula that was built on the
plant growth you can see above the ground. The model gives that formula the plants' whole growth, roots included. Because the formula
bends upward, a somewhat too-large input gives a much too-large herd: if half of grass growth is underground, the model has about three
times too many grazers on open grassland, and so about three times too many dragons there. The same formula also counts insects among
the grazers, which matters most in forest, desert and tundra.

Evidence (dragon-density review round 2, section "What the model should change"):
- McNaughton et al. 1989 (Nature 341:142): "Only processes occurring above ground were included, as comprehensive below-ground
  measurements were too few" (p. 142); NAP is "net above-ground primary productivity" (Fig. 1 caption); the biomass fit
  log B = 1.52 log NAP - 4.79 has a slope "significantly greater than 1" (p. 143).
- The model: vegetation._year's NPP is whole-plant (its `net` output subtracts leaf and fine-root turnover, so fine roots are inside
  NPP); gameattrs takes herb_npp = npp x herb share and graze = (herb_npp + 0.3 x npp x shrub share) x (0.4 + 0.6 x open months / 12);
  prey.wild feeds that to the fit.
- With slope 1.52 an input k times the true NAP gives k^1.52 times the biomass. Above-ground share f = 0.7 / 0.5 / 0.4 gives prey
  x0.58 / x0.35 / x0.25 (sensitivity.py). f has no source on file (wishlist item added).
- McNaughton's B is the whole herbivore level: "Dominance by heterotherm herbivores in forests and homeotherms in grasslands" (p. 143).
  Coe, Cumming & Phillipson 1976's fit is large mammals only but semi-arid Africa only (Fig. 3, p. 349).

Direction and size on dragons: fewer, by x0.25 to x0.6 on open grassland if f is 0.4 to 0.7; smaller where the open-months factor
already cuts the input; forests run the other way (wood and canopy are left out of the model's input but are in McNaughton's NAP).

Options:
- **A.** Apply a sourced above-ground share per plant form to the herb NPP before the fit (needs the source on the wishlist).
- **B.** Leave the input, and say on the review page that prey is biased high on grassland by an unknown factor.
- **C.** Fit big-game biomass on Coe et al.'s large-mammal line where it applies (semi-arid open country) and McNaughton elsewhere.

Lean: A once a source is read; note it on the page meanwhile (done in round 2).
- [ ] fetch a root:shoot production source (wishlist)
- [ ] decide A/B/C

## Updates
- 2026-10-31: Status needs-decision -> done. Lane 90: prey.wild feeds McNaughton only the above-ground share, prey.above(rain) from Gherardi & Sala 2020 (PNAS 117:20038, Fig. 3 fit; ~70% below ground arid, ~35% humid; ln/mm a marked reading). The largest effect of the lane: dry and cold land x0.16-0.35 prey. Cold kinds thin: inbox draft cold-dragons-thin. docs/review/dragon-food-chain/report.md
- 2026-10-30: Created from inbox draft draft-prey-fit-fed-whole-plant-npp.md (found by dragon-density-r2).
