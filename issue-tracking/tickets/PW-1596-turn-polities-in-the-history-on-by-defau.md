---
id: PW-1596
title: Turn polities-in-the-history on by default? States now match the read-out at L6 and L7; steadiness a little under
type: task
status: todo
parent: PW-661
milestone: later
subsystem: peoples
effort: s
impact: high
found_by: lane248
blocked_by: [PW-1597]
relates: [PW-1587, PW-1460, PW-1466]
refs: [docs/review/culture/polities/round21.md, planet/lineages/history/params.py, "planet/lineages/history/polity_live.py::LivePolities._step", "planet/lineages/history/polity_live.py::LivePolities._hem_local", docs/review/culture/polities/round18.md, docs/review/culture/polities/round18/live_run.py, docs/review/culture/polities/round16/measure_v1.py, docs/review/culture/polities/round14/measure.py, "world 4360a3", "world 899985"]
created: 2026-11-09
updated: 2026-11-10
---

## Description
**In plain words.** States can be worked out two ways: inside the history as it runs (the switch `POLITIES_LIVE`, off today), so
states pacify their land, wars move peoples and conquerors' attitudes matter while history happens; or read out after the run
(today's default). The live way has been held back because it gave a third fewer states at L6 and a third more at L7 than the
read-out. Lane 248 (round18.md) found why: the history only let a seat be a state if it was the best city of two rings, and judged
"hemmed in" over the people's whole border rather than around the seat. Both now follow the read-out's rule. All on the same code:

| world, seed | states now, on / off | first state, on / off | same ruler under the nudge, 1,000 years ago / now: on / off |
|---|---|---|---|
| L6 4360a3, 7 | 165 / 174 (95%) | 3,300 / 3,700 ya | 24% / 23% against 27% / 27% |
| L6, 3 | 196 / 187 (105%) | 6,600 / 6,300 ya | 34% / 31% against 30% / 36% |
| L6, 10 | 170 / 213 (80%; 2,000 years ago 96%) | 4,900 / 5,300 ya | (the nudge changes nothing on this seed) |
| L7 899985, 7 | 191 / 193 (99%) | 3,300 / 4,100 ya | not measured |
| L7, 10 | 150 / 146 (103%) | 4,600 / 4,500 ya | not measured |

Before the change, on the same code, L6 seed 7 had 116 states on (67% of off); lane 245 measured 16% of ruled land keeping its
ruler under the nudge now (its code, whose seed 7 runs give the same states as this lane's before-runs). The peoples' shares on and off are within half a point on all five pairs; the largest polity's median over the last 3,000 years
is within 0.3 Mkm² on all five (the widest, L7 seed 7: 0.81 on against 1.08 off).

What is still not equal:
- **Steadiness now** is 4-5 points under off on both seeds the nudge moves (23% against 27%, 31% against 36%); at 1,000 years ago
  it is mixed (3 under on seed 7, 4 over on seed 3). One pair per seed.
- **The calendar**: with the switch on, the first state comes 400-800 years later on 3 of 5 pairs and writing 160-380 years later
  on 4 of 5 (draft `draft-live-tech-calendar-runs-late.md`).

**The choice.** A: turn it on now (one line, `params.POLITIES_LIVE = True`; rebuild runs that show polities), and fix the calendar
after. B: wait for the calendar fix, then turn it on. C: wait until steadiness now is measured over re-rolled nudges and matches.
Lane 248's lean: B. The state counts and the peoples now match, so the live polities no longer change *what* the map shows; the
calendar still changes *when*, and flipping before it would move every founding date on the cards by a few centuries for a
reason that is not history.

**What misleads if never decided.** The live polities (wars that move peoples, conquerors' attitudes, revolts) stay off, so the
state cards and the Polities layer keep showing a read-out that cannot affect the peoples it rules; the round-by-round work on
the switch sits unused.

## Updates
- 2026-11-10: Parked with PW-1597 (three strikes, 11-10): POLITIES_LIVE stays off for v0.3.0. v4 -> later.
- 2026-11-09: Lane 262: not flipped; PW-1597's check (new bar) fails on 3 of 5 pairs on 061c6eca, with a consistent sign (round21.md section 3). No steadiness runs made. Goldens untouched.
- 2026-11-09: Lane 258: not flipped; PW-1597's check fails on all five pairs on 3a52d1bc (round20.md section 3). No steadiness runs made. Goldens untouched.
- 2026-11-09: Lane 254b: not flipped, PW-1597's check fails on 3 of 5 pairs (round19.md section 4). Switch-off calendar moved with 81fc3851: L6 seed 7 first state 3,700 -> 3,400 ya, writing 3,347 -> 3,005; L7 seed 7 4,100 -> 3,700, 4,462 -> 4,305; L7 seed 10 unchanged. Steadiness over re-rolls only started: seed 7 on, nudge A (halflings 0.8 -> 0.9): same ruler 26% 1,000 ya / 21% now; the other 11 nudge pairs were left queued in scratch (lane 254b).
- 2026-11-09: Coordinator 11-09: option B. Fix the late live calendar first (PW-1597), then flip with a re-rolled steadiness check (C) folded into the flip lane.
- 2026-11-09: Created from inbox draft draft-flip-polities-live-on.md (found by lane248).
