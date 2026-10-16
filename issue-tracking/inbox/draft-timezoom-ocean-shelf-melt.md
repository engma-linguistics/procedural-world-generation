---
title: "Time zoom: no ocean-driven ice-shelf loss, so a warm (Eemian-like) start keeps West Antarctica"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: low
found_by: pw367-buttress
blocked_by: []
relates: [PW-367, PW-114]
refs: [planet/timezoom.py, docs/overview.md]
---

## Description
Since PW-367, a marine front is buttressed where the air over the sea beside it is below −5 °C (in full
below −10 °C: Morris & Vaughan 2003's limit of shelf viability). In the model, West Antarctica's seas (Ross,
Weddell) are −15 to −17 °C, so warming the air hardly removes their buttressing.

Earth L6 with the Eemian orbit (the default), West Antarctica's marine cells kept after 20 kyr (of 149):

| start | cells kept |
|---|---|
| dT 0 | 125 |
| dT +2 | 99 |
| dT +4 | 93 |

At dT +4 the Amundsen sector loses none of its 35 cells.

The real Eemian loss (+3–5 m from Antarctica) and today's Amundsen retreat are attributed to warm
Circumpolar Deep Water melting the shelves from below, not to the air. The model's ocean carries only a
surface temperature (`climate.compute`: sst, overturning), so it has no such heat.

What to try: a sub-shelf melt term from the sea's heat at depth, which thins or removes the buttressing
where the water is warm. The heat could come from the overturning's inflow temperature, or from the sea
surface temperature's departure from today's. Either needs the ocean lane's fields.
- [ ] a warm Eemian-like Earth start loses most of the Amundsen sector's marine cells within ~10 kyr, and today's
      orbit at dT 0 doesn't
