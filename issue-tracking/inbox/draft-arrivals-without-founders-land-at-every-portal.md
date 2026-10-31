---
title: "Owner call: with dnd's 8 portals, an arrival without founders lands at every portal (late humans 29% -> 84%)"
type: task
status: needs-decision
parent: PW-917
milestone: v2
subsystem: highlights
effort: s
impact: med
found_by: lane78b
blocked_by: []
relates: [PW-1150, PW-697]
refs: [planet/lineages/history/portals.py, planet/lineages/samples/dnd.toml, tools/peoples_robust/trees/late_humans.toml]
---

## In plain words
The D&D tree now opens 8 portals. Elves and gnomes have a set number of founders, shared out over the portals. Any other people that
arrives from outside has no founders number. It gets a whole founding patch at the first portal and a smaller one at each of the
others, so it arrives about ten times as large. In lane 77's "humans arrive late" test, the humans came through 7 portals. They went
from 29% of all people to 84%, and the gnomes fell from 8% to 0.2%.

## Description
- Measured on world 4360a3, L6, seed 7, one try (lane 77's suite, tree late_humans). Humans' founding range was 0.21 Mkm² on main
  and 2.47 Mkm² on lane 78. Main's portal_mode is off.
- Why: `portals._land_wave` without `founders` seeds today's patch at the first portal and a 3-ring blob at each of the others (PW-697,
  kept from main). Lane 78 set `meta.portals = 8` for the elves' "million through ten portals".
- No stock dnd people is affected today: the only arrivals, elves and gnomes, have founders.
- Options:
  - A. Without `founders`, split today's founding patch over the portals, so the total stays the same however many portals open.
  - B. Without `founders`, use one portal (as before lane 78); many portals only for an arrival that says how many come.
  - C. Accept: arriving through many portals is meant to be strong.
- Lean: A. The number of portals then says where a people lands, not how many come.
