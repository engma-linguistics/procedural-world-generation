---
title: "Time zoom: buttressed fronts ground ice on the shelf seas (Ross), and thin grounding-zone cells still go"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: med
found_by: pw367-buttress
blocked_by: []
relates: [PW-367, PW-241, PW-033]
refs: [planet/timezoom.py, planet/timezoom_kernels.py, docs/overview.md]
---

## Description
PW-367 (option A) holds back 0.8 of a marine front's calving where the sea beside it is cold enough for an
ice shelf (`front_buttress`). Earth L6 at a fixed orbit (`obliquity_amp=0 ecc_mean=0 ecc_100=0 ecc_400=0
orbit_ref=start`), 20 kyr:
- **West Antarctica keeps 125 of its 149 marine cells (84%; 54 before).** It loses the thinnest cells at the
  Ross and Ronne grounding zones, ~200–400 m above flotation (the cells it keeps are ~900 m above). All of
  them go in the first 2 kyr. Their seas are −15 to −17 °C, so they get the full 0.8. The remaining 0.2 ×
  ~700 m/yr still takes ~0.2 of their thickness in one step, and then they float. `buttress=0.9` keeps
  146/149, but Antarctica grows by 4.2 Mkm³ and the sea falls 19 m in 20 kyr.
- **Antarctica grounds on 96 cells of today's ice shelves** (62 of them on the Ross shelf, median depth
  ~500 m): +2.2 Mkm³. Antarctica goes from 25.15 to 26.9 Mkm³.
- **Greenland's region grows by 1.5 Mkm³.**
- **The sea falls 12.6 m in 20 kyr unforced** (before: ~0, because the losses and gains cancelled).

Why the shelves ground: the model has no shelf flow. In a 500-year step the flow pushes ice into a sea cell,
and it piles up past flotation before the floating-ice rule sees it. Without buttressing these new cells
calve again; with it they stay.

Tried and not kept:
- **Also holding back the front's flow into the sea** (in the sia_flow kernel): no real change.
- **Breaking off floating ice at every flow sub-step:** the shelves no longer ground, but the steep gradient
  into the empty sea drains West Antarctica (it keeps 64/149).

What to try next:
- a grounding-line flux condition (Schoof 2007, with buttressing) in place of the SIA flux and the calving
  at marine fronts; or
- a crude shelf: floating ice kept in cold-sea cells, spread thin and calved at its own front.

- [ ] an unforced Earth time zoom keeps >= 90% of West Antarctica's marine cells for 20 kyr without grounding
      on the Ross/Ronne shelves (< ~20 new shelf cells)
- [ ] the unforced 20 kyr sea-level drift stays within a few metres
