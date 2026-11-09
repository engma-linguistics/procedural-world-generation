---
title: Should every tree get the diffuse-light gain (with EPS_SCALE refitted), or only the rainforest tree?
type: task
status: needs-decision
parent: null
milestone: later
subsystem: surface
effort: s
impact: low
found_by: scout232
blocked_by: []
relates: [PW-1518]
refs: ["planet/vegetation.py::DIFFUSE", "planet/vegetation.py::EPS_SCALE", docs/review/climate/diffuse/screens.md, docs/review/climate/diffuse/probe.py, docs/review/vegetation/npp-check/npp_check.py, "Mercado et al. 2009 Nature 458:1014 (NORA 6771)", "Yan et al. 2017 JGR Biogeosci 122:3014", "world 506694 (Earth L6)"]
---

## Description
In plain words: forests everywhere use light better under cloud (Mercado et al. 2009 model it for temperate broadleaf
and needleleaf forests), but PW-1518 gave the gain to the rainforest tree only. Its efficiency was measured at one
Amazon tower under a known sky (diffuse fraction 0.55), so the gain has an anchor there. The other trees' efficiencies
were fitted through EPS_SCALE so Earth's land NPP comes out right under whatever sky they have; adding a gain on top
double-counts unless that fit is redone.

Measured on Earth's observed climate (screens.md, same anchor Df0 0.55 for all trees): temperate box NPP 629 -> 673
(+7%), boreal 346 -> 358, land NPP 62.0 -> 63.5 Pg C/yr (MOD17 ~56), forest 44.6 -> 46.4 Mkm2.

What misleads if never done: cloudy and sunny temperate climates grow the same per unit of light, so a cloudy world's
temperate and boreal forests are under-credited against a sunny one's (small: their Df spread is narrow in the model,
0.52-0.53 on Earth).

Options:
- A. Rainforest tree only (today). Simple; no refit.
- B. All trees, each anchored at a Df where its eps can be read from a tower, and EPS_SCALE refitted on MOD17. More
  correct, more fitting work (temperate boxes, land NPP, then a judge).
- C. All trees with one global anchor and EPS_SCALE refitted to keep land NPP. Simpler than B, less grounded.

Lean: A until a v2 vegetation pass; then B.
