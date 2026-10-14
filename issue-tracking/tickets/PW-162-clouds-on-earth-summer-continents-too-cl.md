---
id: PW-162
title: "Clouds on Earth: summer continents too clear, wet tropics too gloomy, NH winter trade-wind seas too cloudy"
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: low
found_by: clouds
blocked_by: []
relates: [PW-143, PW-019]
refs: [planet/climate.py, tools/earth_check.py, "world dc3732", docs/review/clouds/]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The diagnostic clouds (climate.clouds, PW-143) meet most of the Earth sanity targets in
tools/earth_check.py (annual: Sahara 17%, Southern Ocean 82%, Sc decks 64-70%, ITCZ 66-69%,
W Europe 72%), but some regions miss, mostly where they inherit the rain model's errors:
- Summer continents too clear: Siberia annual 48% (target 60-70); European Russia July 46%;
  land sunshine at 50-80 N is 10-15 points above CRU. The model's continental summer rain and
  vapour are low (Siberia July q/qs ~0.4), so humidity cloud and cumulus stay thin.
- Wet tropics too gloomy for the sunshine record: Amazon January 79% cloud, 23% sunshine
  (CRU 37%); Congo, East Africa and Phuket/Goa-style monsoon coasts 1-3 h/day below CRU, where
  the rain itself is 2-3x too heavy (East Africa, Sahel).
- NH winter trade-wind seas too cloudy: Canary January 73% (ICOADS 49%), Hawaii January 70%
  (57%), California January 78% (65%): the model's January subsidence band sits at ~18 N, so the
  stratocumulus term (stability x sinking) fires over the winter trades.
- E Mediterranean January 70% (40-60): the latitude-belt storminess is high there in winter.
- Arabia 31% (10-25): the model's Arabia is ~3.5x too wet.
What I'd try: a seasonal free-troposphere temperature in the stability measure (the inversion
weakens in winter); let cumulus over land use the (vapour_mixed) humidity of the summer air
mass rather than the kernel's drained vapour. Most of the rest should move with PW-015 (rain).
- [ ] Siberia annual cloud >= 55%, Canary January <= 65%, without moving the passing regions

## Updates
- 2026-10-14: Created from inbox draft draft-cloud-regional-misses.md (found by clouds).
