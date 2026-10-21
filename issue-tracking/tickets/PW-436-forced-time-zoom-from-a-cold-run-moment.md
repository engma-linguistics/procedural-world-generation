---
id: PW-436
title: Forced time zoom from a cold run moment loses ice (+41 m at 20 kyr, up to +141 m) after PW-366
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: pw366
blocked_by: []
relates: [PW-366, PW-030, PW-295, PW-241]
refs: [planet/timezoom.py, planet/icemass.py]
created: 2026-10-19
updated: 2026-10-20
---

## Description
After PW-366 the unforced time zoom stays near a run's start (L6 seed 2 @ 580 Myr: +7 m at 20 kyr, +13 m at
50 kyr). With the default forcing (orbit, CO2, ice albedo; `start=average`), the same moment (sea level
-593 m, 134 Mkm3) rises: +41 m at 20 kyr, +45 at 50, +133 at 100, +68 at 150 kyr (max +141, never below the
start; ice 134 -> 111 Mkm3). On the old code's moment (64 Mkm3) the new time zoom gives -40 / -70 / +36 /
+107 m (min -78, max +113). The run's ice is the extent under the balance averaged over the cycle's orbits
(icemass.cycle_dq: obliquity +-0.85, eccentricity 0.03), so a forced time zoom should swing around its start,
not sit above it. Suspects: the time zoom's real eccentricity/obliquity amplitudes larger than cycle_dq's
(melt is convex, so more spread means less ice), and `average_room` for CO2 / ice albedo (an already-cold
moment has little room left to cool but full room to warm).
- [ ] measure the forced 150 kyr mean sea level from 3-4 cold L6 moments; find which forcing term makes the
  mean sit above the start; fix that side (no scaling to meet)
- needed by PW-030 (real ice-age cycles start from these moments)

## Updates
- 2026-10-20: pw440 survey (L6, 400-600 kyr, default + PW-440 cycle): seed 11 @ 260 / 280 / 300 Myr +346 / +275 / +114 m max (mean +181 / +238 / +103), seed 2 @ 620 / 660 +177 / +218 m, s580 +225 m, s400 -147 m (cold, a new 70-80 N sheet). The cycle leaves between-ice-ages behaviour as it was, so it can't fix this; PW-030's swing-around-the-start criterion waits on this ticket.
- 2026-10-19: pw030 measured it (docs/review/audit/PW-030-handoff.md): on new L6 runs the unforced drift is itself large and moment-dependent (seed 2 @ 580 +40 m, seed 11 @ 400 -67 m at 150 kyr); the CO2 + albedo loop amplifies it ~2.5x to a branch (+210 / -150 m); the orbit alone loses ice by rectification (fast melt, slower regrowth; seed 2 @ 580 eccentricity alone +142 m). The albedo side's room asymmetry (+2 vs -1 C) is gone with the run's tanh rule (PW-030); drift unchanged within 5 m.
- 2026-10-19: Created from inbox draft draft-forced-timezoom-loses-ice-from-run-moment.md (found by pw366).
