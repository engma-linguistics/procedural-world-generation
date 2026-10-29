---
title: "Dry subtropical coasts: three mechanisms, not one (winter return flow vs a too-deep cold high; no frontal rain at low surface humidity; no Andes low-level jet) — pick the plan"
type: task
status: needs-decision
parent: PW-013
milestone: v1
subsystem: climate
effort: l
impact: med
found_by: lane26
blocked_by: []
relates: [PW-998, PW-026, PW-015]
refs: [planet/climate.py, docs/review/base-climate/coasts/README.md, docs/review/base-climate/coasts/probes.patch]
---

## Description
Lane 26's diagnosis is in docs/review/base-climate/coasts/README.md. It used Earth L6 single solves on db7a178a,
with the model's winds against NCEP 850/925 hPa.
- **SE USA, SE China, NE USA and E Australia lose their winter half.** SE USA Oct-Mar rains 93 against 1334 mm/yr and
  its vapour is 3.7 against 17.5 mm. The model blows 1.6-3.8 m/s offshore (the cold continent's high) where NCEP has a
  weak onshore return flow (+0.9..+1.4 m/s).
- **Japan has the vapour but doesn't rain it.** Rain per mm of vapour is 0.3-0.4x observed in both halves.
- **The Pampas lacks the Andes-steered northerly low-level jet** (NCEP -2..-3.4 m/s; the model has a weak
  southerly).

Probes (each one solve):
- Eddy mixing up to 10x: SE USA 36 -> 43%, but B falls to 24.8.
- The Coriolis 1/f land-sea wind: dries SE USA to 11%.
- Shallow winter cold domes: winds toward NCEP, corr 0.691 -> 0.703, exact +1.0, but SE USA only 36 -> 40% and Pampas
  31%.
- Ocean subtropical highs: one-sided they help summers only; two-sided they wet the deserts.
- A wider Andes blocking reach: no effect.
- The best combination gets SE USA 58% and Pampas 42%, with B 23.7 (bar ~26).

Options:
- (a) Commit the shallow cold domes as round 1 (a sound change that improves corr, exact and winds), then design a
  winter frontal-lifting rain term (overrunning along the storm track) and a mountain-channelled low-level jet, as
  separate rounds.
- (b) Split PW-998 into three tickets (winter return flow and frontal rain; the Pampas jet; Japan's rain efficiency)
  and schedule them, the cold domes first.
- (c) Park the coasts for v2's moisture-transport proposal.
Lane 26's recommendation: (b), with the cold domes first. The SE USA / Pampas 60% bar isn't reachable by one change
without B falling below 26.
