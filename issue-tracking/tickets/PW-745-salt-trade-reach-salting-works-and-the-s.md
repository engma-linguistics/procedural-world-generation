---
id: PW-745
title: Salt trade reach, salting works and the sea-food goods are not read by any way of life yet
type: story
status: done
parent: PW-692
milestone: v3
subsystem: timezoom
effort: m
impact: med
found_by: fun9
blocked_by: []
relates: [PW-732, PW-723, PW-739]
refs: [planet/lineages/seafood.py, planet/lineages/land.py, planet/lineages/brief.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-732 built the goods (`salt`, `fish`, `shellfish`, `sea_mammals`, `_salt_km`, `_salt_kind`) and the brief's `salt` and `fish` sections, but:
- no `[[use]]` row in the dnd tree names them, so no people's habitat follows the fisheries or the salt (fisher-forager ways of life, PW-723);
  the herbivore peoples' craving for salt (`body.salt = craving`) pulls nothing;
- `_salt_km` is a land distance only: a people on a coast two hundred km of sea from a salt lake still reads the land graph. A trade pass
  (brief `trade_reach`, PW-692 item 2) should turn "far from salt" into "traded, dear" per people, and let boats shorten routes;
- salting works (fish sauce, cured fish) need salt AND fish at the same coast; the brief only gives both numbers. A joint "cured fish" marker
  is cheap once a use reads it;
- sea salt is boiled at .35 on every ice-free damp coast, which makes `_salt_km` small on every coast; whether boiling needs a fuel check
  (the fuels layers: no wood, no boiling) is a judgement call.
- [ ] a [[use]] row for fishers and a salt use for the craving peoples, measured on 1df1c3 / 3e9e7d
- [ ] trade: salt reach per people

## Updates
- 2026-10-24: Status todo -> done. Merged 615c1ff: salt reach v0 (cost-distance, rivers, contact zones, cap); brief v7. Follow-ups PW-796.
- 2026-10-24: fun13: tried a mild `[[use]]` salt pull (weight 0.3) for the ruminant peoples in seven_meals.toml on 1df1c3: mean km to salt 307 -> 320 (antelope-kin), 482 -> 494 (cervid-kin), wish 0.635 -> 0.615, one draw each: no effect, so not kept. Fisher ways already read fish and shellfish through WAYS (PW-723). Trade reach, salting works and the boiling-fuel check are untouched.
- 2026-10-24: Created from inbox draft draft-salt-trade-and-sea-food-uses.md (found by fun9).
- 2026-10-24: fun21: first pass: planet/lineages/salt_reach.py, cost-distance to salt (rivers x0.5, contact zones x0.6, 450 km cap) and the brief's salt.reach own/traded/cut-off shares; salt-poor = a quarter of the land cut off (was: mean over 300 km). 104de8 dwarf: mean 419 km, own 43% / traded 30% / cut off 27% -> poor; antelope-folk 289 km, cut off 11% -> not poor. No salting works or new goods. Follow-ups in draft-salt-reach-follow-ups.
