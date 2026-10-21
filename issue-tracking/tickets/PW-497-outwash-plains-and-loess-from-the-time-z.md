---
id: PW-497
title: Outwash plains and loess from the time zoom's glacial imprint
type: task
status: todo
parent: PW-037
milestone: v1
subsystem: timezoom
effort: m
impact: med
found_by: pw037
blocked_by: []
relates: [PW-037, PW-096, PW-092]
refs: [planet/timezoom/sim.py, planet/finish.py, docs/proposals/glacial_carving.md]
created: 2026-10-21
updated: 2026-10-21
---

## Description
The time zoom now erodes, carries and drops glacial debris (PW-037), but all of it lands as till where the
ice melts. In reality a large share leaves the margin in meltwater: sandur / outwash plains down the
proglacial rivers, and the fines blow downwind as loess (PW-096, merged into PW-037; also desert loess).

What to try:
- At each step, a share of the debris released at a margin cell (melt) goes down the bare ground's
  drainage (the finished world's or a cheap steepest-descent route on the frame's bed) and settles over
  ~100–300 km as outwash (record `glacial_outwash`, m, per frame like `glacial_till`).
- Loess: the outwash's silt share, lifted where the outwash plain is dry and bare in the cold months, carried
  downwind by the climate's winds (jet / surface wind) and dropped over a few hundred km (a world layer
  `loess`, m; deserts the same from dune/playa sources). The zoom can then flatten and soften the ground
  under thick loess.
- [ ] outwash plains below long-lived margins in a 1 Myr time zoom; loess sheets downwind of them
- [ ] volume conserved (erosion = till + outwash + loess + debris in the ice)

## Updates
- 2026-10-21: Created from inbox draft draft-glacial-outwash-and-loess.md (found by pw037).
