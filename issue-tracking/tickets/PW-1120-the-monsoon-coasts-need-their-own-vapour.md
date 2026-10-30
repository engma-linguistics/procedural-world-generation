---
id: PW-1120
title: The monsoon coasts need their own vapour supply before the land-sea inflow can carry only its low layer's vapour (PW-1099's partner)
type: task
status: needs-decision
parent: PW-015
milestone: v2
subsystem: climate
effort: xl
impact: med
found_by: lane62
blocked_by: []
relates: [PW-1099, PW-1100, PW-1094, PW-1097]
refs: [planet/climate.py, docs/review/base-climate/moisture-inflow-ascent/, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The model's summer sea breeze on a continental scale brings too much of the air's vapour inland
(PW-1099). Fixing that dries the interiors as it should, but it also dries the US south-east, the Pampas, India and
SE China to about half. In the model those coasts get their rain from that same flow. Lane 62 tried two "make it
rain where the air rises" partners. Both are sound and need no tuning:
- rain from the inflow's convergence (PW-1100);
- the ascent on the subtropical highs' western flanks, which the planet's spin implies.
Neither gives the coasts their rain back, because the coasts are short of vapour, not of lift. So the partner has to
be a supply.

Measured (lane 62, Earth L6, main -> inflow depth; SE USA Apr-Sep box):
- The box is a through-flow: S face +3853 -> +2546 mm/yr, N face -4189 -> -2690.
- The column dries: PW 25.2 -> 18.0 mm (NCEP 33.5), q/qs 0.55 -> 0.40.
- The land's evaporation falls with its rain (717 -> 215; NCEP 1686), and showers fall 82 -> 62% of the rain.
- Lift added on top (convergence and western-flank ascent, L6): SE USA 318 -> 320-334 (GPCC 1328, main 636),
  Pampas 171 -> 172-190 (944), r 0.666 -> 0.661-0.668.

Options (each its own design round, with the same Earth gate):
- (i) A land-sea friction contrast in monsoon_wind. Onshore air slows and turns over rough land, so its vapour
  piles up at the coast instead of blowing 1000-2500 km inland. **Needs a meteorology source on land and sea surface
  drag** (or the surface wind's ratio to the geostrophic and its cross-isobar angle over each). docs/references has
  none; the owner may fetch one (a boundary-layer textbook chapter).
- (ii) Moister source seas. The Gulf and W Atlantic subtropics rain 520 vs 1240-1330 mm and hold PW 32 vs 39 mm.
  That is PW-015's one-layer column under the bulk exchange (option A there; large).
- (iii) The land's vapour residence: 4.1 days against ~9 observed, so imported vapour rains before it spreads.
  Changing it is a rate retune, the owner's call.
- (iv) The Pampas also need PW-1094's mountain-channelled low-level jet.
After the partner, apply the patch in docs/review/base-climate/moisture-inflow-ascent/ (PW-1099's inflow depth, PW-1100's convergence ascent) and judge
everything as one.

Placement (coordinator 10-30): v2, unless the owner asks for (i), which would be the next single round.
- [ ] with the inflow depth on: SE USA and the Pampas not below main, log-rain r not below 0.70, B not below 25

## Updates
- 2026-10-30: Created from inbox draft draft-monsoon-coasts-need-vapour-supply-not-lift.md (found by lane62).
