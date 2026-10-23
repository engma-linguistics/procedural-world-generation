---
id: PW-447
title: "Time zoom: ice-age endings at the agreed strength are slow (30-75 kyr) and stall on cold extra ice"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: pw440
blocked_by: []
relates: [PW-440, PW-030, PW-436, PW-435]
refs: [planet/timezoom/cycle.py, planet/timezoom/sim.py, docs/review/audit/PW-440-handoff.md]
created: 2026-10-20
updated: 2026-10-23
---

## Description
PW-440's cycle (melt x up to 1.8, calving x 2, CO2 release up to ~90 ppm, only beyond the last
interglacial's ice) gives s400 (L6 seed 11 @ 400 Myr) ~100-kyr pacing, but its endings take 30-75 kyr
and stall with 20-112 m of extra ice left: a new 70-80 N sheet whose surface summers are -11 C, which no
degree-day factor can melt. On the tests' L4 icehouse an ending gives back only 3.6-5.3 m more in 20 kyr
than without the cycle. Earth never gets big enough to try (PW-435).
Options:
- A. Leave the strength; fix the drift that makes the polar sheet (PW-436) and Earth's depth (PW-435)
  first, then re-measure. Lean.
- B. Strengthen the ending beyond the agreed numbers (e.g. melt_max 2.5, both the orbital response and
  the degree-day factor, or the boosts on the interglacial footprint's extra thickness too). Risks the
  Antarctica-melting failure PW-030 saw with a global boost.
- C. Make a stalled ending's leftover part of the interglacial (tried: ratchets the cold drift, s400
  mean -117 m), not recommended.
- [ ] decide; then s400 and Earth endings <= ~15 kyr with swing >= 80 m

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: pw460: with the PW-460 margin the zoom's endings rise to 5-7 per 600 kyr on Earth with 0 backstops, against main's 2 (obs: 2 backstops). Depends on PW-461.
- 2026-10-20: Created from inbox draft draft-timezoom-ending-strength.md (found by pw440).
