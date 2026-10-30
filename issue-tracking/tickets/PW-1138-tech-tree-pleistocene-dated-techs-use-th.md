---
id: PW-1138
title: "Tech tree: Pleistocene-dated techs use their track's rate (0.02-0.03 a kyr), so bread, fermentation and beer reach few peoples"
type: task
status: needs-decision
parent: PW-675
milestone: null
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-69
blocked_by: []
relates: [PW-1109, PW-1011, PW-1122]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words: a tech dated 11.6 kyr or older keeps its Earth date as a hard floor and is then invented at its track's slow
default rate (one chance in 30-50 per kyr). For food that matters: bread (14.4 kyr), fermentation (13), beer (13) are found by
only 1-3 peoples a world, and the rest wait for contact; in 4 runs x 2 draws 26-29 of 50 peoples knew bread at the present.
Pottery (20 kyr) was the worst: 1-4 finds a world and, in one draw, nobody before 0.06 kyr ago, which held back kilns, copper and
writing for the whole world. Lane 69 gave pottery a rate override from the catalogue's band (Earth's 7 origins from 20 to 5 kyr:
a median wait ~9 kyr after the floor, rate 0.09); villages already had one (0.12, PW-1011). PW-1109 (bread and fermentation's
cutoff) was closed as superseded by the rework; this is what is left of it.

Options:
- A: per-tech overrides from each tech's band, by hand (as pottery): bread, fermentation, beer, storage, honey hunting.
- B: a rule: a floored tech with several Earth origins gets its rate from the band (median origin date minus the earliest, as the
  median wait for the anchor people), the way soft techs get theirs from the lag. The catalogue's `earth_origins` and the hunt's
  origins_checked give the band; the anchor check can test it.
- C: leave it: these are old techs and contact carries them.
Lean: B (one rule, uses the catalogue as intended: the brief called the origins "the band").

## Updates
- 2026-10-30: Fun lane 70: option B built. band_wait: a floored tech with 2+ dated Earth origins (`origins_kyr`, added from the catalogue on 61 rows) waits after its floor as the median origin did (42 rows qualify; pottery's hand rate 0.09 is now the rule's; beer 4 kyr, 0.20/kyr).
  One origin (bread, wild cereals) keeps the track rate and spreads by the faster contact. Living peoples knowing bread 62% -> 72%, fermentation 62% -> 74%, beer 0% -> 73% (the tree's ceiling here ~72-74%). Bread's world first stays late (9.7 kyr vs 14.4): draft.
- 2026-10-30: Created from inbox draft draft-techtree-floored-techs-track-rate-slow.md (found by fun-lane-69).
