---
id: PW-440
title: "Time zoom: the cold feedback branch is rigid (CO2 clipped, ice area saturated), so glacials never terminate"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: high
found_by: pw030
blocked_by: []
relates: [PW-030, PW-436, PW-031]
refs: [planet/timezoom.py, docs/review/audit/PW-030-handoff.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-030's analysis (`docs/review/audit/PW-030-handoff.md`): the time zoom's CO2 + ice-albedo loop amplifies
any drift ~2.5x and sends a run's moment to one of two branches. On the cold branch (L6 seed 11 @ 400 Myr:
-150 m, 24% of land iced) dT sits at a flat -2.25 C for 400 kyr: CO2 is clipped once the ice is 60 m past
the start (`average_room` 0.5 x `co2_max`), and the ice's area is at the geography's limit, so the albedo
term can't change either. With no feedback left, a summer-sun peak melts 15-40 m of margin and the ice
regrows: a heartbeat, never a termination. Lakes, dust and a 10 kyr bed lag (tried) change nothing; only a
~1.8x stronger orbital response (`insol_k` 0.45) gives cycles, and that melts Earth's interglacial
Antarctica, so the sensitivity must come from the glacial state.

Options:
- A. Smooth CO2 saturation (tanh in the ice excess, as the albedo now is) instead of the hard clip, with the
  full Earth range (~-2.5 C) shared around a run's start rather than cut at half. Cheap; keeps a feedback on
  the cold branch. May not be enough alone.
- B. CO2 that follows the (lagged) global or southern-ocean temperature, not only the ice volume
  (solubility, sea ice, ventilation): an insolation peak's warming releases CO2 before the ice has gone,
  which is the observed order at terminations. More physics, needs a timescale choice (~1-3 kyr).
- C. Leave CO2 and look at the sheets' own carried air (separate draft): the margins of a big glacial sheet
  may be over-protected in summer.
Lean: B, with A's smooth saturation, tested on the handoff's three L6 moments and Earth before anything
else; the target metrics are PW-030's.

## Updates
- 2026-10-20: Status needs-decision -> todo. Owner decision 2026-10-20: a three-mode cycle (Paillard 1998 / Huybers 2011): between ice ages, building, ending, with hysteresis (once an ending starts it runs to completion). An ending starts when the ice is big enough AND a summer-sunshine peak beats a bar that falls with the glacial's age; the orbit picks the timing and nothing forces a length. Inside an ending: (1) melt sensitivity rises smoothly with the extra ice, 1.0x between ice ages up to ~1.8x for big sheets; (2) CO2 release of +80-100 ppm over ~5-10 kyr (fixes the clipped-CO2 lock); (3) faster calving for marine-based ice. Thresholds come from each planet's own sunshine range. Backstop: past ~2x a typical length, the next peak ends it; log how often it fires. Done: swing >= 80 m, slow builds and fast endings, Earth's interglacial ice unchanged (~8-9% of land), unforced start still holds. Sea-ice starvation parked as PW-441. Follows the PW-442 refactor.
- 2026-10-20: Created from inbox draft draft-timezoom-cold-branch-rigid.md (found by pw030).
