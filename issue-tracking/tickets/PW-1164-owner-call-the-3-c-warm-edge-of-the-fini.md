---
id: PW-1164
title: "Owner call: the +3 C warm edge of the finish band, against Earth-like climate variance"
type: task
status: in-progress
parent: null
milestone: v2
subsystem: climate
effort: xs
impact: med
found_by: lane80
blocked_by: []
relates: [PW-1161]
refs: [docs/review/base-climate/finish-drift-l80/README.md, planet/highlights.py, docs/review/base-climate/warm-edge-l81/]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. A finished world's present must sit between 6 C colder and 3 C warmer than pre-industrial Earth.
Across 18 test worlds, the finish temperatures spread with a standard deviation of about 3.7 C around a middle of
about 0 C. That spread comes from slow, Earth-like wandering of volcanic CO2 and of erosion, made larger by ice and
methane feedbacks. It is not a bug. With that spread, the +3 C edge sends about 1 world in 5 over the warm side,
and we see 4 of 18. Earth's own record swings more than this: the last 540 Myr ran from about 11 to 36 C, and the
Cenozoic from about +14 to -6 C against today. So the model is not too variable. Nothing is changed. This is only
for you to decide whether the edge is where you want it.

Numbers (lane 80, lane 75's K judge, L6, roll 0.0005), from a Gaussian at median 0 and sd 3.7 C:
- band -6..+3 (today): ~74% inside, ~21% too warm (observed 4/18 warm);
- a warm edge near +4.7 C would leave ~10% too warm;
- moving the median to the band's centre (-1.5 C) would give ~78%, but the cold tail then reaches the hard
  frozen-over criterion, so lane 80 doesn't recommend steering for it.
- The finish window (10 Myr) can't rescue much: finish T is red (source autocorrelation 0.71 at 10 Myr), so the
  window holds only ~1 C of spread.
- [ ] Owner: keep +3 C, or move the warm edge (e.g. +4 to +5 C)

## Updates
- 2026-10-30: lane81 (branch): warm edge +5 C in `highlights.HUMAN_RANGE` (passrate3/4 and screen.py import it); setting "require permanent ice" (Params.finish_require_ice; `planet make --require-ice --tries N`; New planet form checkbox); lane 75's K judge re-scored: 13/18 pass at +5 (12/18 at +3), scripts in docs/review/base-climate/warm-edge-l81/.
- 2026-10-30: Status needs-decision -> in-progress. Owner D19 (2026-10-30): the warm edge of the finish band moves to +5 C. Caveat: a user setting that refuses worlds with no permanent ice (rerolling as needed; a reroll or three is fine).
- 2026-10-30: Created from inbox draft draft-warm-finish-band-edge.md (found by lane80).
