---
id: PW-1203
title: "Proposal: a people's density follows the way of life it actually lives, era by era, not one hand number for its whole history"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: lane84
blocked_by: []
relates: [PW-1149, PW-1147, PW-974, PW-1180]
refs: [planet/lineages/history/model.py, planet/lineages/history/peoples.py, planet/lineages/history/growth.py, planet/lineages/prey.py, planet/lineages/samples/dnd.toml, docs/review/peoples-why/report.md]
created: 2026-10-31
updated: 2026-11-03
---

## In plain words
Humans are two thirds of all people mainly because each human square kilometre holds about seven times as many people as everyone
else's, not because humans hold most of the land (they hold about a fifth of what peoples hold). The preset gives humans a farmers'
density (10 per km², farmers 12) for their whole 200,000 years, while elves have 1, orcs 1 and dragonborn 2, whatever they do for a
living. A people's numbers per km² should come from how it lives at the time: foragers thin, gardeners denser, plough farmers densest.
Then any people that takes up farming gets farmers' numbers, and humans are not farmers before they farm.

## Description
Measured by lane 84 (docs/review/peoples-why/report.md, section 1; world 4360a3, dnd, one try per seed):
- Base seed 7: humans 65% of people on 21% of the held range, 9.8 people per km² of their range against 1.4 for all others.
  Holding presences as they are, one density for everyone would put humans at 35%.
- Human lines at x0.3 density: humans 67% -> 35% (seeds 7, 10, 13: -32, -32, -33 points); human range unchanged (73 -> 82 Mkm²).
  Five-people cut: 83% -> 58%, range 107 -> 108. So density works through the count, not the contest: INVADE 0 + DENSITY_PUSH 0
  moves the five-people cut by -0.6 points.
- Today: `History.dens` is one number per line for the whole run (model.py:102), times a static productivity field read through the
  line's land-use shares (model.py:113-116, prey.py:121-140). Lane 78's era (forager / horticulturalist / agrarian, growth.py:31-46)
  changes growth rates only.

Options:
- A. Density from the era's way of life: a forager, horticulturalist and agrarian density per people (defaults by way, overridable),
  switched by growth.py's era as it already is for the life tables; the productivity field read with that era's shares.
- B. A only for the arithmetic of the count (population), the contest's density terms kept on the authored number.
- C. Keep one number, but set the preset's numbers by way of life (D20 lever 3: elves as forest gardeners 3-5, dwarves as mountain
  farmer-miners 6-8), leaving the 200 kyr of farmer-dense humans.
Lean: A; it is the general form of D20 lever 3 (PW-1149) and fixes humans counting as farmers before farming.
- [ ] dnd and the lane 77 suite rerun, the human share and the elves' and dwarves' reported against today

## Updates
- 2026-11-03: Status needs-decision -> done. Closed 11-03: option A built. growth._set_era_density and growth.ERA_DENSITY set a people's density by era (forager / plough farmer); overview 2.26 'Density follows the era' (lane 83, owner D20 lever 3).
- 2026-10-31: Created from inbox draft draft-density-follows-way-of-life-over-time.md (found by lane84).
