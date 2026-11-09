---
id: PW-1587
title: With polities in the history on, still about half to three quarters as many states, and the map less steady when nudged
type: task
status: done
parent: PW-661
milestone: v4
subsystem: peoples
effort: m
impact: high
found_by: lane241
blocked_by: []
relates: [PW-1456, PW-1460, PW-785]
refs: ["planet/lineages/history/polity_live.py::LivePolities._step", "planet/lineages/history/polity_live.py::LivePolities._places", "planet/lineages/history/polity_live.py::LivePolities._confederations", "planet/lineages/history/polity_live.py::LivePolities._second_places", "planet/lineages/settlements.py::derive", "planet/lineages/polities.py::_site_tables", docs/review/culture/polities/round16.md, docs/review/culture/polities/round16/diag.py, docs/review/culture/polities/round16/measure_v1.py, docs/review/culture/polities/round14/measure.py, "world 4360a3", "world 899985", "scratch l241 runs 02a90b dbd75c 0119b9 1dbb64 (on), 6418c8 14ae84 4c6c89 863ee2 (off)"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** Lane 241 (round16.md, the ticket made from draft-live-polities-stay-small.md) gave the history's polities the read-out's confederations, second peoples' towns as
seats and the town threshold by stage. With the switch on, the largest polities now reach about the same size as with it off, on
three L6 seeds (world 4360a3). The peaks are 3.11, 2.05 and 3.27 Mkm², against 2.28, 1.56 and 3.35 off. The medians are a bit
lower: 0.29, 0.90 and 1.43, against 0.40, 1.01 and 1.79. Two things are still worse than off:
- **Fewer states:** 78, 100 and 100 now, against 120, 134 and 203 off. Likely cause: the ledger's towns keep their people for a
  while after their cell stops being the best of its rings (growth lag, slow decline). The history recomputes its central places
  every century and keeps an incumbent only through HOLD, so it has fewer cities at once.
- **Less steady under PW-1460's nudge** (one pair, seed 7, L6): at the present 11% of ruled land has the same ruler, against 16%
  off; the nudge's top 10 states kept 0/10, against 4/10 off.
Not yet measured at L7: a pair on world 899985 (seed 7, base and nudge, this code) was started in lane 241's scratch (tags L7s7f,
L7n7f under l241/data7) and may have landed.

**What misleads if never done.** Flipping `POLITIES_LIVE` (v0.4) on these numbers would roughly halve the count of states on the
cards and make the map shift more when a tree is nudged, against today's read-out.

Try first: give the history's central places memory (a seat's size eases toward its new place over a few centuries, as the
ledger's sites do), rather than a threshold. Then re-measure on/off at L6 seeds 3, 7 and 10, plus the L7 pair.
- [ ] L7 seed 7 on/off with lane 241's code: largest median and peak, states, nudge steadiness
- [ ] states with the switch on within the switch-off spread on the same seeds
- [ ] nudge steadiness on no worse than off over at least two seeds (re-rolled draws), then a needs-decision to flip the switch

## Updates
- 2026-11-09: Status todo -> done. Lane 245 (3e89ffd9): live central places read settlements._site_factor; states on/off L6 58-77% of off, L7 126-141%. Humans' L7 share was PW-1558 (same on and off). Remaining gap -> PW-1594; humans -> PW-1593.
- 2026-11-09: Lane 245 (round17.md): the L7 humans' jump (65% on vs 40% off) was a code mix-up, not the switch: lane 234's off run predates PW-1558 (12f38974), which moves the peoples from 38 kyr ago; on today's main, off gives humans 66.0% (seed 7) and 56.4% (seed 10), on 65.5% and 56.9%; shares match within 1.3 points on 5 pairs. The state gap was the ledger's site factor, not its memory (decomposition: no memory gives more states; no site factor 120->74). Built: the history's places use settlements._site_factor (behind the switch). Now, today's main: states L6 s7/3/10 116/144/123 vs off 174/187/213; L7 s7/10 243/206 vs off 193/146; largest medians close; nudge steadiness L6 s7 same ruler 22%/16% vs off 27%/27%. No flip; remaining gap in draft-live-polities-states-and-steadiness-after-site-factor.md.
- 2026-11-09: Coordinator 11-09: lane 241's L7 pair (world 899985, dnd, seed 7, branch 24f33270, switch on, run 16b49e) vs lane 234's off 0a1c30: first state 3,300 vs 4,100 ya; states 2,000/1,000/0 ya 89/121/148 vs 50/89/122; largest last 3 kyr median 0.77 vs 0.46, peak 1.23 vs 2.33 Mkm2, >=2.3 in 0/31 vs 1/31; nudge (2b7069 vs 19e53f) same ruler 27%/19% (1,000 ya/now) vs 19%/20%. But humans' share now 65.3% on vs 39.6% off: the switch reshapes the peoples heavily at L7. One seed: L7 on now matches or beats off except the peak; L6 still short on state count.
- 2026-11-09: Created from inbox draft draft-live-polities-fewer-states-l7-check.md (found by lane241).
