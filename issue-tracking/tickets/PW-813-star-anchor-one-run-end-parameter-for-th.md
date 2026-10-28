---
id: PW-813
title: "Star anchor: one run-end parameter for the star and the plant calendar, set by every direct Simulation caller and stored for replays; guard runs longer than the star's age; an extension keeps the anchor"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: tectonics
effort: s
impact: med
found_by: star-anchor-audit
blocked_by: []
relates: [PW-791, PW-807, PW-557]
refs: [planet/tectonics/params.py, planet/timeline.py, tests/helpers.py, tools/scorecard.py, tools/ice_diag.py, tools/sealevel.py, tools/supercontinent.py, docs/review/base-climate/star-anchor-audit/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Audit items 10 and 11 (docs/review/base-climate/star-anchor-audit/README.md).

An end-anchored star needs the run's end. `Simulation` doesn't know it today:
- `timeline.simulate` sets `flora_end = myr`, and so do tests/helpers.py, tools/scorecard.py:60 and
  tools/ice_diag.py:56;
- tools/sealevel.py:67, tools/supercontinent.py:91 and ~20 tests build `Params()`, which falls back to
  `earth.FLORA_END` = 1000.

Do:
- Use one field, e.g. `run_end` replacing `flora_end`, for both the star (PW-791) and the plant calendar
  (PW-807), so the two fallbacks can't disagree.
- Set it in every direct caller, and store it in run meta so `slice` replays reproduce.
- Update the goldens on purpose.

Bounds:
- make.py allows up to 4000 Myr, and `simulate --myr` has no bound. T > 4570 Myr gives a negative star age, so
  guard it: clamp, or refuse with a message.
- At 4 Gyr the anchored start is -50 C raw at full Gough (-26 at 0.45). The owner wants such runs habitable, which
  is PW-791's thermostat job; note it in the help text.

PW-557 (extend a run): an extension must keep the original anchor. The extension is the ruled "future offset", and
re-anchoring would change the run's past.
- [ ] one run-end field used by star and flora; direct callers set it
- [ ] T > 4570 guarded
- [ ] PW-557 note added on intake

## Updates
- 2026-10-24: v1-finish-10: done in the branch. params.run_end (0: the run's length, set by timeline.simulate; earth.now_myr the one reader, RUN_END_DEFAULT 1000 for direct callers) replaces flora_end for star and flora, stored in run meta params; check_star refuses runs longer than the star's age; direct callers (tests/helpers, scorecard, ice_diag, health, test_store) set it. PW-557 note: an extension keeps run_end (the extra time is star_now_offset_myr's future). docs/review/base-climate/v1-finish-10/README.md
- 2026-10-24: Created from inbox draft draft-run-end-param-star-and-flora.md (found by star-anchor-audit).
