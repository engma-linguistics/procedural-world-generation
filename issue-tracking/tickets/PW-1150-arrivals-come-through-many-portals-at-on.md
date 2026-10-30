---
id: PW-1150
title: Arrivals come through many portals at once, with a founder count per arriving people
type: task
status: todo
parent: null
milestone: v2
subsystem: highlights
effort: s
impact: med
found_by: lane76
blocked_by: []
relates: [PW-697, PW-917]
refs: [planet/lineages/history/origins.py, planet/lineages/history/portals.py, planet/lineages/samples/dnd.toml, planet/lineages/history/params.py]
created: 2026-10-30
updated: 2026-10-30
---

## In plain words
Elves, gnomes and tritons come from other planes. The owner would like them to be able to arrive in force: for example a million
elves through ten portals, rather than one group in one spot. Most of this already exists. Portals are built, and an arriving
people already founds at every portal it can live near. But the D&D preset has portals switched off, and each portal seeds only
a small patch. This task turns the portals on and adds one number per arriving people: how many came through.

## Description
- Today: dnd.toml `portal_mode = "off"`, `portals = 1`. With portals on, `_origin_new` seeds the first site within
  `FOUNDER_KM` (400 km, lane 73) and each other portal 3 rings (~37 cells ≈ 0.12 Mkm² at L7, ~70 k elves at density 1).
- Proposal: a per-arrival `founders` (total people) is split across the portals that can hold the people. Each portal's seed grows
  ring by ring over its free room (lane 73's free-room siting, inside the 700 km disc) until it carries its share, as `_jump`
  grows a blob to the viable number. An optional per-arrival `portals` override (tritons through one sea gate).
  Default `founders` should reproduce about today's size.
- Lane 73's momentum edge measures range mass against its own lagged mass (a ratio), so a big wave keeps the edge as long as a
  small one does. No change is needed there.
- [ ] dnd.toml: `portal_mode = "sites"`, `portals` ~6–10 (owner to confirm the count)
- [ ] `founders` in spec, the workbench and the editor schema
- [ ] screen on a few rolls: elves', gnomes' and tritons' share of people and cells led, before and after

## Updates
- 2026-10-30: Created from inbox draft draft-portal-arrivals-in-force.md (found by lane76).
