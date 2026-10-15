---
id: PW-232
title: "Clouds on Earth, rest of PW-162: NH winter trade-wind decks too cloudy, wet tropics too gloomy, E Mediterranean January"
type: task
status: todo
parent: PW-013
subsystem: climate
effort: m
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-162, PW-015]
refs: [planet/climate.py, tools/earth_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Branch smalls2 fixed PW-162's summer continents (storm cloud on land now goes with the air's humidity, not its cube: Siberia annual 49 -> 56%, NH land sunshine 50-80 N 5-6 points nearer CRU, RMS 15 -> 14). Left:
- **Winter trade-wind seas too cloudy:** Canary annual 68% (ICOADS 51), January ~70%; Hawaii January 83% (57-70). Cause: the sinking belt (`sink` in `_season_inputs`) sits 25 deg from the rain belt and moves with it, so in January it is centred at 18.6 N, right over Hawaii and the Canaries, where the stratocumulus term (stability x sinking) fires. Tried: making the belts follow half the rain belt's shift (`sink_follow` 0.5): every cloud region in range and ITCZ Atlantic fixed, but the summer Mediterranean clouds over (E Med July 24 -> 37%, target 5-25), subtropical sea bands 3-4 points worse, Kottek exact 39 -> 38%. Not taken. A cleaner try: the stratocumulus deck's stability against a seasonal free troposphere (the winter inversion is weaker and higher; the deck peaks in summer-autumn off California and the Canaries), leaving the rain's sinking belt alone.
- **Wet tropics too gloomy:** Amazon 82% (65-80), land sunshine 0-10 N 38% (CRU 54), 10 S-0 33% (48): deep cloud from rain that is itself 2-3x too heavy in places (East Africa, Sahel; PW-015).
- **E Mediterranean January** 65-69% (40-60): high winter latitude-belt storminess there.
- [ ] Canary January <= 65% and Hawaii January <= 70% without the summer Mediterranean clouding over

## Updates
- 2026-10-15: Created from inbox draft draft-clouds-winter-trades-and-tropics.md (found by smalls2).
