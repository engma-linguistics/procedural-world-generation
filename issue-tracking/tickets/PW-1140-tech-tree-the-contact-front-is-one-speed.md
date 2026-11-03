---
id: PW-1140
title: "Tech tree: the contact front is one speed everywhere; corridors and barriers (habitat, seas, mountains) should change it"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: culture
effort: m
impact: low
found_by: fun-lane-70
blocked_by: []
relates: [PW-1137]
refs: [planet/lineages/techtree.py, docs/references/techtree/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words: a new tech now spreads from a people to its neighbour like a slow wave, about 1 km a year, the speed at which
farming crossed Europe. On Earth such waves ran several times faster through easy country and much slower through hard country,
and the model doesn't yet know the difference.

What lane 70 built: `techtree.contact_rate` is 2 ln 2 v / sqrt(taker's range), v = `contact_speed_km_yr` = 1.0. The delay is
drawn once per pair of peoples (one front for all its techs), x 1 / the tech's spread, x the border share and the taker's
openness. Evidence read: Neolithic 0.6-1.3 km/yr (Pinhasi et al. 2005); pottery among foragers 1.2 km/yr in steppe and temperate
forest against 0.2 elsewhere, 3.3 against 0.5 in the Mediterranean zone (Jordan et al. 2016, Table 1), so the corridors were
6-7 times faster.

What would make it better:
- The pair's delay comes from the shared border's land (biome, relief, a sea crossing; the contacts record has border km per
  frame, not its kind). The tech catalogue's sea-going techs could open sea routes.
- Overlapping peoples (contacts' mixed_pct high; most pairs here share many cells) should learn faster than ones that only
  touch. Today the taker's whole width counts either way.
- A readable source on copper smelting's spread across Eurasia, to check the speed on a craft tech (none open was found).

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-contact-front-geography.md (found by fun-lane-70).
