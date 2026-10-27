---
title: Storm giants fill ~9 Mkm2 of cool open sea (~47,000 of them) instead of keeping to coasts
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-37
blocked_by: []
relates: [PW-924, PW-775, PW-779]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/samples/seven_meals.toml, "world 2a7385, dnd 7000-7003"]
---

## Description
PW-924 (owner) puts storm giants on coasts, sharing them with bronze or blue dragons. The trees still give them `realm = "sea"` with
`elev_m = [-3500, -300]` (PW-775/PW-779: all open water in the depth band, `temp_c = [6, 16]`). On 2a7385, dnd seeds 7000-7003, they
hold ~9.5 Mkm2 of sea, ~47,000 giants at 0.005 per km2 in 3 pockets. That makes them the most numerous megafauna by far, and they are
not on the coasts.

Options:
- A: `realm = "coast"` (the shore ring, as the merfolk) with the same temperature band. They become a counted coastal megafauna of
  many small pockets, which meets the PW-924 table.
- B: keep the sea realm but narrow the depth band to the shelf edge (e.g. [-1500, -100]).
- C: leave as is.

Lean: A. It is a tree change, so it needs the owner's yes.
- [ ] storm giants in many coastal pockets, counted in the hundreds to low thousands on a showcase world
