---
title: Live dragon realms ~28 % short on three of fifteen dates; flip POLITIES_LIVE anyway or one more mirror?
type: task
status: needs-decision
parent: PW-661
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lane281e
blocked_by: []
relates: [PW-1596, PW-1687]
refs: [docs/review/culture/polities/round28.md, docs/review/culture/polities/round27.md, docs/review/culture/polities/round26.md, "planet/lineages/history/polity_live.py::DragonCultures", "planet/lineages/demes.py::Demes._cut", "planet/lineages/demes.py::Demes._fuse", "planet/lineages/cultures.py::Cultures._contacts", "planet/lineages/polities.py::_core", docs/review/culture/polities/round28/replay.py, docs/review/culture/polities/round27/per_people.py, docs/review/culture/polities/round26/measure.py, "runs a1c6ed 1a7fae 91c10c 8e517f a80cfe (scratch, deleted; numbers in round28.md)"]
---

## In plain words
Turning on "states inside the history" (the switch POLITIES_LIVE) waits on one check: the history must seat about as many dragon
realms as the after-the-fact read-out does. It now nearly does: 12-26 dragon realms where the read-out has 16-26 (round 26 had only
4-6). On 12 of 15 measured dates it is within 25 %; on three it is about 28 % short (L6 world 4360a3 seed 10 at 1,000 years ago,
17 against 24; L7 world 899985 seed 7 at 1,000 years ago and now, 16 against 22 and 12 against 16). States, first states and writing
pass. The brief said stop after one more pass, so the switch is still off.

## Description
Lane 281e (round28.md) measured the five pairs on f11aeeac: dragons avg5 live vs read-out on the same history: L6 s7 -23 / -8 / +6 %,
L6 s3 -1 / +9 / +2 %, L6 s10 -18 / -28 / -12 %, L7 s7 -18 / -29 / -28 %, L7 s10 -20 / -12 / -10 %. States against round 26's off
runs: worst -13.9 % (L6 s7 at 1,000 ya). Deterministic (91c10c = 22afa5).

Options:
- **A (lean): flip now.** Three dates at ~28 % against a ~25 % bar; the shortfall is a few realms on a map of ~20, and no hard
  failure. The flip is one commit (round28.md section 5). Keep this ticket for the remaining gap.
- **B: one more mirror pass first.** Still unmirrored: the demes' fusion (Demes._fuse, FUSE_KM x LINK_KM / JUMP_KM: touching demes
  of small summed diameter fuse after PERSIST frames), which changes later gap splits. On L7 s7 about half the gap is fewer
  cultures (replay: 34 against 41) and half is fewer of them seating a realm (near settled land, polities._core / DRAGON_KM), so a
  pass would also have to look at the seat. Cost: ~3 h of runs.
- **C: loosen the bar to ~30 %.** Same outcome as A, stated as a threshold change.

- [ ] Coordinator picks A, B or C; if A, flip in its own commit and re-run the tests and goldens.
