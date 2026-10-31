---
id: PW-1170
title: Check the "require permanent ice" threshold (0.5% of the surface) and the existing 1% land-ice floor
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: climate
effort: xs
impact: low
found_by: lane81
blocked_by: []
relates: [PW-1164]
refs: [planet/highlights.py, planet/tectonics/output.py, planet/make.py, viewer/start.js]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The new setting "Require permanent ice" (New planet form, `planet make --require-ice`) refuses a finished
world with no ice that survives the warmest month. "Permanent ice" is my judgement call: land ice, plus sea whose warmest
month stays below freezing, covering at least 0.5% of the planet's surface (`highlights.PERM_ICE_MIN_PCT`). Earth today is
about 10% of the surface. Say if you want a different number.

Two things to know:
- The finish checks already demand land ice of at least 1% of the land (about 0.35% of the surface at 35% land), so
  a world with no land ice at all already fails the finish today. The new setting is the stricter floor (0.5% of the
  surface, counting sea ice too) and it adds the re-roll: with it on, a world with none in the last 10 Myr is replaced by a new
  seed, up to `tries` (default 3) times. With it off, behaviour is unchanged.
- On lane 75's 18 draws (L6, main physics) the land-ice part alone is under 0.5% of the surface at the picked moment for 3, and
  in the whole last 10 Myr for 1 (l6fix seed 639472). Sea ice was not recorded in those runs, so these counts are upper bounds.

- [ ] Owner: keep 0.5% of the surface, or pick another floor
- [ ] Decide whether the 1% land-ice floor of the standard finish should stay now that the setting exists

## Updates
- 2026-10-30: Created from inbox draft draft-permanent-ice-threshold.md (found by lane81).
