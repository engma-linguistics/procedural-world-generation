---
title: With polities in the history on, states still under off at L6 and over it at L7, and the map less steady when nudged
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: m
impact: high
found_by: lane245
blocked_by: []
relates: [PW-1587, PW-1460, PW-1466]
refs: ["planet/lineages/history/polity_live.py::LivePolities._step", "planet/lineages/history/polity_live.py::LivePolities._places", "planet/lineages/history/rule.py::StandIns.circumscribed", "planet/lineages/polities.py::_hemmed", "planet/lineages/polities.py::derive", "planet/lineages/history/tech_live.py::LiveTech", docs/review/culture/polities/round17.md, docs/review/culture/polities/round17/decomp.py, docs/review/culture/polities/round16/measure_v1.py, "world 4360a3", "world 899985", "scratch l245 runs 489391 a8bae4 219933 b50f2c 4d3e0a 92ff72 (on), 38b40b d60e31 dc21ac 1d1592 7bf29c b08650 (off)"]
---

## Description
**In plain words.** Lane 245 (round17.md) gave the history's central places the settlement ledger's site factor (harbours, rivers,
fresh water, fertile ground, passes), the part that carried the state count. On today's main, with the switch on, the peoples'
shares and the largest polity's median now match switch off on 5 pairs. Two things still do not:
- **States:** L6 world 4360a3 seeds 7 / 3 / 10 have 116 / 144 / 123 states now, against 174 / 187 / 213 off; L7 world 899985 seeds
  7 / 10 have 243 / 206, against 193 / 146 off. Under at L6, over at L7.
- **Steadiness** under PW-1460's nudge (L6 seed 7): 16% of ruled land keeps its ruler now, against 27% off.

Ruled out: the size of the places. The ledger re-made the way the history now sizes its places gives 191 states now on L6 seed 7,
about off's own 174 (round17.md section 2), so the gap is in what the history does with its places. Also ruled out: the ledger's
memory (removing it gives more states, not fewer). Candidates to test first, cheapest first:
1. seats keyed by cell (`c<cell>`): a central place whose best cell moves one ring starts a new polity without incumbency or its
   luck, unlike the ledger's site ids; likely also the steadiness gap;
2. the hemmed-in term: the history reads the people's whole border (`StandIns.hem`), the read-out the seat's own two rings;
3. the live calendar running late (first state 400 years later than off on L6 seed 7).

**What misleads if never done.** Flipping `POLITIES_LIVE` on these numbers would make the state count on the cards a third lower
at L6 and a third higher at L7 than today's read-out, and make the map shift more when a tree is nudged.
- [ ] states with the switch on within the switch-off spread at L6 and L7 on the same seeds and code
- [ ] nudge steadiness on no worse than off over at least two seeds, then a needs-decision to flip the switch
