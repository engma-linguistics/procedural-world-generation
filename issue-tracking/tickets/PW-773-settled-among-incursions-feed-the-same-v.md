---
id: PW-773
title: Settled-among incursions feed the same valence as displacement; should co-residence alone read as feared (PW-769 follow-up)
type: task
status: todo
parent: PW-767
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: fun15
blocked_by: []
relates: [PW-769, PW-756, PW-767, PW-768, PW-661]
refs: [planet/lineages/contacts.py, planet/lineages/reputation.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-769 added the `settled_among` incursion kind (presence of a people rising >= `SETTLE_RISE` 0.15 in one stored frame in cells another people still leads; same
episode/threshold machinery as displacement; `meta.contacts.incursions[].kind`). `reputation.py` reads both kinds identically (a `feared` / `despised` candidate with the
kind in its basis text), as the owner said a ruling-minority rise counts as an incursion.
Open: the original lean was that settling among should feed `feared` only when the old people also lost lead share, with pure co-residence left to the polity pass (PW-661), and a
weaker valence than conquest. If a world shows many mild `settled_among` rows souring memories too much, either scale `loss_scale` by 0.5 for the kind or gate on lead loss.
- [ ] Count `settled_among` rows per run on a few worlds/draws before deciding; SETTLE_RISE 0.15 and the shared INCURSION_* thresholds are first guesses (one world, tries 1).
- [ ] Not tuned to make any people called devils (PW-767) or any attitude beyond `aggressive` (PW-768).

## Updates
- 2026-10-24: Status needs-decision -> todo. Parked under PW-767 (historical linguistics, later).
- 2026-10-24: Created from inbox draft draft-settled-incursions-reputation-gate.md (found by fun15).
