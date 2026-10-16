---
id: PW-379
title: Scattered start stays dispersed with slow plates and an old ocean (74 Myr, sea -185 m) through 500 Myr
type: task
status: wontdo
parent: null
subsystem: tectonics
effort: m
impact: low
found_by: run-lane (PW-328)
blocked_by: []
relates: [PW-328, PW-293, PW-191]
refs: [planet/tectonics/setup.py, planet/tectonics/motion.py, planet/tectonics/events.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-328's setup fix (each continent whole on one plate, boundaries in the ocean) fixed the scattered
start's first 100 Myr: 8 L6 seeds (1-8, 500 Myr), ocean age 54 Myr and sea -25 m over 0-100 Myr
(supercontinent start: 50 Myr, -15 m; before the fix 58-93 Myr at 100 Myr, sea -54..-182 m).
But after that the scattered runs drift away from the supercontinent-start runs (8-seed health
sweep, same code), medians of per-seed medians:

| window | ocean age (Myr) | sea (m) | speed (cm/yr) | landmasses | largest |
|---|---|---|---|---|---|
| scattered 150-500 | 68 (60-98) | -147 | 3.7 | 12 | 16% |
| supercontinent 150-500 | 54 (48-74) | +6 | 4.3 | 6 | 27% |
| scattered 300-500 | 74 (58-117) | -185 | 3.7 | 11 | 16% |
| supercontinent 300-500 | 50 (46-66) | +43 | 4.5 | 8 | 21% |

The scattered world never assembles (11-16 landmasses all along) and its plates stay slow. It isn't
simply "dispersed worlds have old oceans": in the supercontinent-start runs, frames after 150 Myr with
11+ landmasses have a *younger* ocean (51 Myr, 4.4 cm/yr, sea +44 m) than assembled ones (57 Myr).
Not checked: per-plate continent share (scattered: ~half the plates carry continent at the start vs
1-3 for the supercontinent; keels feel 2.5x drag), and whether many small continents jam trenches
(collisions instead of subduction) or keep plates from meeting the margin-subduction rule.

Options:
- (A) Accept: a scattered start makes a different planet (dispersed, slower plates, Earth-like
  ~64-74 Myr ocean, a lower sea), all inside the health envelopes (ocean age 25-120, sea -250..+300).
- (B) Investigate the mechanism (motion.py keel drag per plate, events.py margin-subduction
  thresholds with small continents) and nudge whichever is unphysical.
- (C) Setup: fewer, larger scattered continents (the fbm field gives 19-39 pieces, many tiny);
  only if (B) shows the small pieces are the cause.
Lean: A for now (scattered isn't in the recipes or the sweep); B if the owner wants scattered
starts as a supported mode.

## Updates
- 2026-10-16: Status needs-decision -> wontdo. Coordinator 2026-10-16: accept (a start choice, not in the health sweep or showcases; a dispersed world with slow plates is a legitimate planet). Documented here.
- 2026-10-16: Created from inbox draft draft-scattered-regime-old-ocean.md (found by run-lane (PW-328)).
