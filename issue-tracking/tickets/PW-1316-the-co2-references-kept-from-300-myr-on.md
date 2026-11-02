---
id: PW-1316
title: The CO2 references, kept from 300 Myr on, lock in whatever transient the spin-up ended on
type: task
status: needs-decision
parent: null
milestone: null
subsystem: climate
effort: m
impact: med
found_by: lane-115
blocked_by: []
relates: [PW-558, PW-559, PW-576, PW-1295, PW-1158]
refs: ["planet/tectonics/earth.py::global_temperature", docs/review/tectonics/margin/pw1295-note.md, docs/review/tectonics/margin/envdraw.py, tests/test_envelopes.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the CO2 balance compares outgassing and weathering against what they were during the planet's
start-up (learnt until 300 Myr, then kept). If the start-up ends during a lull in volcanoes or a burst of weathering,
the planet keeps "remembering" that as normal, and afterwards CO2 piles up or drains away for the rest of the run.

Numbers (pw1295-note.md section 4, test_envelopes' world, L5, 400 Myr, 40 runs over two code arms): the end
temperature follows the 300-400 Myr imbalance against the kept references with correlation 0.80. The worst case
(seed 2 with PW-1295's bound) learnt the source 17% low and the sink 42% high and ran to 28.8 C. With main's code
seeds 12 and 20 end 8 and 6 C warmer than their other arm in the same way.

This is the reference scheme PW-558/559 B chose on purpose (kept references let a long cold era's deficit keep
counting). Options, for the owner:
- [ ] A: learn the source's reference as a longer mean over the spin-up (e.g. its whole 100-300 Myr mean, not a
  100 Myr e-folding that weights its end)
- [ ] B: keep it as is (the trips are rare: 1 of 40 left the test band here)

## Updates
- 2026-11-02: Owner 2026-11-02 asked why B over C (isn't outgassing part of the thermostat?); answered in chat: the thermostat is the weathering sink's climate response; the references are only the yardsticks; drifting yardsticks (C) were tried in PW-576 and erased real trends within a few hundred Myr. Awaiting his pick.
- 2026-11-02: Created from inbox draft draft-frozen-co2-references-lock-in-spin-up-transients.md (found by lane-115).
