---
id: PW-468
title: "Time zoom start: offer the glacial phases available at a moment (on: interglacial / building / glacial maximum / ending; off) in the API and viewer"
type: story
status: todo
parent: PW-470
milestone: v2
subsystem: viewer
effort: m
impact: med
found_by: pw462
blocked_by: []
relates: [PW-462, PW-429]
refs: [planet/api.py, planet/server.py, viewer/index.html, planet/timezoom/run.py, planet/timezoom/sim.py]
created: 2026-10-20
updated: 2026-10-23
---

## Description
Owner idea in PW-462: when a time zoom is started, list the phases available at that moment and let the
user pick. Today `/api/timezoom` takes {run, t, kyr}; the viewer's button posts that; `find_timezoom` reuses
a zoom with the default knobs; the orbit's phases are fixed per (seed, Myr), so a moment always starts in
the same phase.

Proposal (needs draft-tz-window-spinup.md first; then cheap):
- The run says whether the moment cycles: "on" where the run's cold-phase extent differs from its
  persistent (interglacial) extent by more than ~10 m of sea level, "off" otherwise
  (draft-run-ice-cycle-mean.md stores both per keyframe), plus "era start" / "era end" where the next or the
  previous keyframe crosses that line (draft-tz-era-start-end.md).
- For "on", the phases are picked by *where the window starts in the orbit*, not by changing physics: the
  spin-up runs once over e.g. 400 kyr and the window starts at the first time its state matches the request
  (interglacial: sea level in the top 15% of the spin-up's range, outside an ice age; glacial maximum: bottom
  15%; building / ending: the cycle's mode). The orbit is analytical, so the window's later forcing simply
  continues from that time.
- API: `phase` in {auto, interglacial, building, glacial, ending, era_start, era_end}; 400 with the list of
  available phases when the request's isn't. `find_timezoom` keys on it. The viewer shows a small picker
  with only the available ones, and the summary names the phase the window started in.
- [ ] api + server + viewer picker; tests for the request parsing and the phase selection on the L4 icehouse

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created from inbox draft draft-tz-phase-picker.md (found by pw462).
