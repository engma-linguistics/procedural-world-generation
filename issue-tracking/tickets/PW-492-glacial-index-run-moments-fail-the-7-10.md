---
id: PW-492
title: "Glacial index: run moments fail the 7/10 bar because their ice at I = 0 isn't the zoom's balance"
type: task
status: needs-decision
parent: PW-244
subsystem: timezoom
effort: m
impact: high
found_by: pw471
blocked_by: []
relates: [PW-471, PW-436, PW-461, PW-462, PW-470]
refs: [docs/review/audit/PW-471-handoff.md, docs/review/audit/PW-471-spinup.patch, planet/timezoom/cycle.py, planet/timezoom/sim.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-471 (the glacial index) passes on Earth but not on run moments; the stop rule was reached after two
attempts. Numbers: L6, 400 kyr, default knobs, 10 cold moments of 4 fresh L6 runs (seeds 5, 3, 2, 11;
scratch store, `PW-471-handoff.md`). A moment passes if it cycles (>= 2 endings), every glacial maximum
is at most 1.5x its sea-level target below the start, and no interglacial stands more than 1.5x the
target above it (no runaway melt).

- Attempt 1, the index as specified (I = 0 is the run's climate): 0/10 pass. All 10 cycle (2-3 endings
  each, 91-118 kyr apart), but 8 drift away from their start: interglacials +15..+198 m on 8 (the zoom
  sheds the run's ice), -73..-171 m on seed 5 @ 260 (it grows a sheet). Closest: seed 3 @ 620 and
  seed 11 @ 420 (maxima -58..-85 m against targets of 52-53 m, i.e. up to 1.6x; interglacials up to
  +60 m). Main's code on the same moments (its PW-440 cycle) is worse on 9 of 10: mean sea level
  +45..+186 m (-74 on seed 5 @ 260), against -147..+154 with the index (+4 and -20 on the closest two).
- Attempt 2, plus a 40 kyr spin-up at I = 0 and the mean orbit (the zoom as a window on its own
  interglacial, PW-462 item 3; patch `docs/review/audit/PW-471-spinup.patch`, +7% run time; measured at 6 C): 3/10
  pass (seed 5 @ 520, seed 3 @ 200 and @ 500). The spin-up itself moves the sea level -51..+98 m and
  hasn't converged on several moments.

Why (measured, `index=off`, the mean orbit, so I = 0 throughout): 5 of 10 moments drift more than
25 m in 50 kyr (+16..+101 m; seed 5 @ 520 +94, seed 2 @ 500 +101, seed 3 @ 200 +84), still drifting at
50 kyr. Calving and shelf melt outrun the surface balance (e.g. seed 2 @ 500: +1800 m sea-level
equivalent of surface balance against 2030 m lost to the sea). A global cooling doesn't hold that ice:
-4 C still loses +60 m (seed 2 @ 500, seed 3 @ 200) in 50 kyr. This is PW-436 / PW-461 B(2): the
run's ice rule has no calving, so its marine and coastal ice isn't the zoom's balance. Earth is near
balance at I = 0 (-10..+5 m in 50 kyr), which is why Earth passes.

Second, on moments with lots of free cold land the glacials run deep: seed 5 @ 260, seed 3 @ 620 and
seed 11 @ 420 reach 1.6-2.2x the target (the target, 2 km of ice over the snowline land, ignores ice
that grows beyond it, as the Laurentide does on Earth; Earth itself is ~1.0-1.2x).

Options:
- (A) Fix the run/zoom budget gap first (PW-436/PW-461: give the run's ice rule the zoom's marine
  losses, or the zoom a run-consistent coast); then the index as is. Physical, the right fix, but it
  touches the run (run lane) and is l effort.
- (B) Ship the index plus the spin-up (patch ready): every zoom starts in its own interglacial; the
  zoom's I = 0 ice is then the zoom's balance, not the run's (the run's ice is reported as the
  spin-up's sea-level change). 3/10 today; the remaining drift needs a longer spin-up (cost) or (A).
- (C) Ship as is (Earth good, run moments drift as on main) and reword the run bar for v1.
- Also decide the target's form: a planet-relative target that counts the land the sheets can spread
  onto (e.g. land within a few C of the snowline) instead of the snowline land alone.

Lean: (C) now for v1 (the index is no worse than main on run moments and fixes Earth), with (A) as the
real fix, scheduled in the run lane; (B) only if the showcases need run moments before (A).

## Updates
- 2026-10-20: Created from inbox draft draft-glacial-index-run-moment-drift.md (found by pw471).
