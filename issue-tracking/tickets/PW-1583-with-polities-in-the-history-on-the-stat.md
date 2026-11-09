---
id: PW-1583
title: With polities in the history on, the states stay small (largest 0.44 Mkm² against 2.28 with the switch off)
type: task
status: done
parent: PW-661
milestone: v4
subsystem: peoples
effort: m
impact: high
found_by: lane238
blocked_by: []
relates: [PW-1575, PW-1456, PW-1434, PW-785, PW-1449]
refs: ["planet/lineages/history/polity_live.py::LivePolities._step", "planet/lineages/polities.py::_confederations", "planet/lineages/polities.py::WIDE_BY", "planet/lineages/polities.py::derive", docs/review/culture/polities/round15.md, docs/review/culture/polities/round15/check.py, docs/review/culture/polities/round14/measure.py, "world 4360a3", "scratch run f4fb14 (on)", "scratch run 6418c8 (off)"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** Since PW-1575 the viewer, the state cards and the religion read-out show the polities that fought inside the
history when the switch (`params.POLITIES_LIVE`) is on. On the one pair measured (world 4360a3, L6, dnd tree, seed 7, 30 kyr, same
code, switch on vs off: round15.md), those polities are much smaller and fewer than the read-out draws with the switch off. Over the
last 3,000 years the largest state or empire has a median of 0.21 Mkm² on (0.40 off) and peaks at 0.44 Mkm² (2.28 off). No state is
ever over 1 Mkm² on (up to 4 at once off). There are 68 states now (120 off), and the first one forms 2,500 years ago (2,800 off).
Writing is about the same: 11 of the 12 largest peoples write on, against 12 of 12 off.

**What misleads if never done.** Flipping the switch (v0.4: "states fight inside the history") would shrink every world's empires
about fivefold at their peak. The size check (Taagepera 1997's 2.3 Mkm² floor, PW-1456) would fail by a wider margin, and the cards
would show no empire on the scale of Rome. The switch cannot be flipped until this is understood.

**Candidates (not diagnosed).**
- The history has no confederations (polities' step 1b, `_confederations`). WIDE_BY gives confederations the stacked reach past
  STATE_MAX_KM, so a whole route to large polities is missing.
- Seats are the history's central places (SHARE x hinterland heads), not the ledger's towns. These may make fewer and smaller cities,
  so fewer seats pass the state gate.
- Fewer states means fewer state-on-state conquests, the only other way past STATE_MAX_KM (WIDE_BY "conquest").
Check first: count the read-out's confederations on the off run, and its states whose reach came from WIDE_BY.

One seed on L6 only. Lane 234's L7 queue (seeds 7 and 10, on and off) will say whether this holds at L7. Re-run its measure.py on
those runs: since PW-1575 its "readout" row on a switch-on run is the live map.
- [ ] diagnosis on the L7 pairs: which candidate explains most of the gap
- [ ] with the switch on, the largest polity over the last 3 kyr is within the spread of the switch-off read-out on the same seeds

## Updates
- 2026-11-09: Status todo -> done. Lane 241 (24f33270): cause = history lacked confederations and second-people town seats (states capped at one city-state's reach); both added behind the switch, plus stage-aware town threshold and a refugee NaN fix. L6 seeds 7/3/10 largest polity peak now 3.11/2.05/3.27 Mkm2 (off 2.28/1.56/3.35). Switch stays off: fewer states (50-75% of off) and less steady under the nudge; follow-up ticket taken in.
- 2026-11-09: Created from inbox draft draft-live-polities-stay-small.md (found by lane238).
