---
id: PW-462
title: "Deep dive: the run's ice as a cycle average and the time zoom as a window that can start in any glacial phase (or an era's start or end)"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-461, PW-030, PW-033, PW-435, PW-447, PW-460, PW-459, PW-440, PW-366, PW-438, PW-422]
refs: [planet/icemass.py, planet/tectonics/earth.py, planet/timezoom/, planet/orbit.py, tests/test_timezoom_cycle.py]
created: 2026-10-20
updated: 2026-10-26
---

## Description
Owner framing (2026-10-20). There are two timescales:
- **Ice-age eras** (icehouse periods) last tens of Myr and show up on the run's timestep.
- **Glacial cycles** (~100 or 41 kyr; the cold stretch is what most people call "an ice age") happen inside an era, dozens per run step.

The framing has three parts:
1. **The run's ice should stand for the average over the cycles within a step.** Today it is the balance with the step's single climate, plus hysteresis. Because ice grows slowly and collapses fast, that balance is icier than the true average and can never deglaciate. This is the cause of PW-461.
2. **A time zoom is a window, not a continuation that has to hold the run's state.**
   - It may start in any phase: glacial maximum, mid-melt or interglacial, set by the planet's orbit at the start time.
   - Its start and end don't have to match the run's ice; its average over the zoom should.
   - The current consistency test, start-of-zoom drift against a 25 m bar, may be testing the wrong thing.
3. **Era starts and ends.** Where the run's climate crosses into or out of an icehouse within or next to a step, the zoom could offer to show the era starting or ending. Otherwise it offers "on" (cycling) or "off".
   - Possible UI: when a zoom is started, list the phases available at that moment and let the user pick.

The task: a read-only deep dive into the existing code, reporting what this framing changes in the run (`earth._ice_pass`, `icemass`, CO2 and weathering, sea level, the health checks' cold-era bars) and in the time zoom (`cycle.py`, `forcing.py`, `sim.py`, start-up, the consistency tests, `finish.orbit_dt`, output and viewer). For each piece it reports:
- what it assumes now;
- what would change;
- the cost (effort);
- what it unblocks.

PW-461 option B and the PW-460 margin are re-judged under the framing. Write-up: `docs/review/audit/ice-framing-deep-dive.md`, plus inbox drafts for each piece of work it proposes, ranked. No physics implementation.

Done when:
- the write-up exists, with a recommended order of work that can realistically clear the ice-age problem;
- it says how each existing ice-age ticket changes (close, fold or keep);
- it gives a test or acceptance definition for "run ice = cycle average" and for "zoom average matches run";
- it flags anything that makes this framing a dead end.

## Updates
- 2026-10-26: Merged PW-313: the run's ice rule can't hold Earth's Antarctica at today's climate (dT 0); it decays to ~0.1% of the surface. (PW-900 backlog reorg).
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: pw462: deep dive in docs/review/audit/ice-framing-deep-dive.md. Zoom-as-window holds: every icy run moment starts at an edge of its zoom's range (time means -68..+137 m off the run), so test the window mean, not start drift. Run-as-cycle-mean only half holds: on main the run is the cycle's interglacial edge on moderate moments (L5 fixture: run -19 m, 8 orbital states' own equilibria mean -83, zoom mean -87), but on deep moments (L6 s11@400 -252 m) the states agree with the run and the zoom's +94 m mean is ~40 m rule/budget gap (unforced) + 20 orbit + 30 feedback reference. The PW-460/459 freeze is not averaging (all states -340..-371 m; zoom sheds +101 m): marine budget. Ranked drafts: tz-mean check (s), run marine budget (m), run cycle-state mean with the feedback swing (l), re-apply PW-460/459 (m), zoom spin-up window (m), phase picker (m), bars wording (xs), era start/end (m).
- 2026-10-20: Created from inbox draft draft-ice-as-cycle-average-framing.md (found by daniel).
