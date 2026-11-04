---
title: "Rift sliver test fails once the plants change: a rift leaves a 2.4% continental piece where the floor is 3%"
type: task
status: todo
parent: null
milestone: later
subsystem: tectonics
effort: s
impact: med
found_by: lane185
blocked_by: []
relates: [PW-1261]
refs: [tests/test_rifts.py::test_rifts_leave_no_continental_slivers, "planet/tectonics/events.py::piece_ok", "planet/tectonics/events.py::sliver", "planet/tectonics/events.py::split", "planet/tectonics/params.py::rift_min_piece", planet/vegetation.py, docs/review/climate/npp/round3.md]
---

## Description
**In plain words.** When a rift splits a continent, each piece should carry either almost no continent or at least
3% of the planet's surface (no thin slivers). A test checks this on a short L4 run (seed 1, 400 Myr). With lane 185's
plant change (herbs' roots respire, FUEL_MIN 200), the run's coastlines come out a little different, and one rift
leaves a piece with 2.4% of the surface: 0.0238 against the test's allowance of under 0.0040 or over 0.0285
(0.95 x rift_min_piece). The test passes on main 21072a23 and fails on lane 185's branch. Nothing in the rift code
changed, so the plants only uncovered it.

Where it comes from, likely: `piece_ok` / `sliver` judge the pieces on the plate's own grid (`cont_cells`), and the
test measures them on the world cells before the split. The test comment allows "a few cells" for the mapping; here
the gap is about 16 cells of 2562 (0.0062 of the surface). Either the plate-grid count and the world-cell count of
a piece can differ by that much (then the check in `split` reads the wrong count), or the piece is a real sliver
that `piece_ok` let through.

What breaks if never done: the not-slow suite stays red on the branch that carries the plant change, and if the
check really reads the wrong count, planets keep occasional 1-3% continental slivers that the rule says should not
exist.

- [ ] Find which count is wrong for this split (print both for the failing piece on seed 1 at L4).
- [ ] Fix the count or the rule; leave the test's thresholds alone unless Daniel rules on them.
