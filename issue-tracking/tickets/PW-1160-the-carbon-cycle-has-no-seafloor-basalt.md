---
id: PW-1160
title: The carbon cycle has no seafloor (basalt) weathering sink
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: low
found_by: lane75
blocked_by: []
relates: [PW-1142, PW-865]
refs: [planet/tectonics/earth.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Rock on land isn't the only thing that pulls CO2 out of the air. Warm seawater circulating
through the young ocean floor also reacts with the basalt and stores carbon as carbonate veins. The model leaves
this out. It's a small sink on Earth, about 7% of the total, so adding it would steady the climate only a little.

Lane 75's gate for PW-1142 put a number on it and the coordinator parked it: in a cold era it changes the sink by
~2%, which isn't worth the effort for v1. Constants, from Krissansen-Totton & Catling 2017 (Nat Commun 8:15423),
Tables 1-2:
- Modern seafloor dissolution 0.225-0.675 Tmol C/yr against a posterior outgassing of 6.6 (4.2-9.6) Tmol/yr:
  ~7% of the silicate sink (2-17%).
- Arrhenius on the pore water: Ea 75 kJ/mol (90% 45-106; Coogan & Dosso 2015 give 92). Pore T = deep-water T
  + 9 K. Deep T = 1.02 x surface T - 16.7 K (their fit). Deep water can't go below freezing (-1.8 C), so the cold
  side falls by at most ~27%.
- It scales with outgassing^beta, beta 0.47 (90% 0.05-0.94: weakly constrained). pH dependence gamma 0.27 on
  [H+]; as a CO2 exponent, mu 0.23 (Brady & Gislason 1997, which K-T&C quote).
- Estimated effect on the model: the thermostat's loop gain goes from ~11 to ~10.3 C of dT per e-fold of source.

Their same posterior gives the continental Te as 34 K (17-48). That's ~0.03/K, and the model's realised
continental slope (0.04-0.05 per C of dT, lane 75's l75/fd.py) is already as strong. So don't make the land's
kinetics steeper to compensate.
- [ ] A seafloor term in co2_stock's sink behind a Params switch, normalised to the balance so its share is ~7%

## Updates
- 2026-10-30: Created from inbox draft draft-seafloor-weathering-sink.md (found by lane75).
