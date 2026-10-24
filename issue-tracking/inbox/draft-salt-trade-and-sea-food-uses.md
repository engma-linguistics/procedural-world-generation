---
title: Salt trade reach, salting works and the sea-food goods are not read by any way of life yet
type: story
status: todo
parent: PW-692
milestone: v3
subsystem: timezoom
effort: m
impact: med
found_by: fun9
blocked_by: []
relates: [PW-732, PW-723, PW-739]
refs: [planet/lineages/seafood.py, planet/lineages/land.py, planet/lineages/brief.py]
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
