---
title: "Time zoom as a window: spin up from the run's state, then start wherever the orbit puts the cycle; the cycle's interglacial footprint and the feedbacks' reference from the run's mean"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: high
found_by: pw462
blocked_by: []
relates: [PW-462, PW-436, PW-447, PW-030, PW-429]
refs: [planet/timezoom/sim.py, planet/timezoom/cycle.py, planet/timezoom/forcing.py, planet/orbit.py, docs/review/audit/ice-framing-deep-dive.md]
---

## Description
Today a time zoom *continues* the run: `_Sim.__init__` takes the run's ice as the state at t = 0, measures
sea level, CO2 (`Forcing.co2_target`: excess = -sl / 120 from the start, `average_room` 0.5) and the ice
albedo (`ice_frac0`) from it, and the cycle (`cycle.Cycle`) takes the start as the interglacial: `sl_ig` = 0,
and `ig_ice` (the footprint the ending's boosts never touch) = the start's ice. So if the run's ice is the
cycle mean (PW-462), the start's glacial share of it is protected from every ending, and the CO2/albedo
references sit at the mean while the window starts at some other phase.

Under the framing the zoom is a window:
1. **Spin-up.** Integrate S kyr (default 200, at least one eccentricity cycle; or the planet's own longest
   orbital period) from the run's state *before* the window, with the same knobs, and discard it. The window
   starts at whatever glacial phase the orbit has reached. The orbit phases already differ per moment
   (`orbit_phases(seed*1000 + round(at))`), so different moments start in different phases.
2. **References from the run, not from the window start.** CO2 and albedo anomalies against the run's mean
   (the spin-up's mean, or the run's persistent + mean-cycling split once draft-run-ice-cycle-mean.md lands);
   `sl_ig` and `ig_ice` from the run's persistent (interglacial) ice when the run provides it, else learned in
   the spin-up (the highest sea level outside an ice age).
3. **Report** the window's phase at its start (mode, extra ice, the summer-sun percentile) in the run.json
   meta and the viewer's summary, and the window's mean against the run's (draft-tz-mean-matches-run-check.md).
4. No nudge to force the mean: if the spun-up mean misses the run's by more than the test's tolerance, that is
   a run/zoom physics mismatch to fix, not a dT correction to add. (A diagnostic dT that would close the gap
   may be *printed*, as a size of the mismatch.)

Cost: +S kyr of zoom per request (at L6 ~1/3 more for a 600 kyr zoom with S = 200). Frames are not stored for
the spin-up. Earth keeps its observed start (today's ice is a real interglacial): `start=interglacial` skips the
spin-up.
- [ ] spin-up in `_Sim` (knob `spinup`, kyr; 0 = today's behaviour for tests)
- [ ] cycle footprint and feedback references from the run / spin-up
- [ ] phase at start reported; tz_mean table re-measured
