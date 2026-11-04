---
id: PW-1460
title: After keyed draws, a small nudge still moves about half the ruled land to another people; find which step carries it
type: task
status: todo
parent: null
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: lane182
blocked_by: []
relates: [PW-1459, PW-1434]
refs: [docs/review/culture/polities/round6.md, docs/review/culture/polities/round5.md, "planet/lineages/polities.py::derive", "planet/lineages/settlements.py::build", "planet/lineages/techtree.py::keyed", "world 899985 (time zoom fc5311) at L7, dnd seeds 7 and 10 (scratch runs, deleted)"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** PW-1459 keyed the tech tree's, the settlement ledger's and the polities' random draws, so a nudge no longer
redraws the tech calendar. Lane 182 re-ran lane 180's nudge check (halflings among humans, wish weight 0.8 -> 0.9, world 899985 at
L7, seeds 7 and 10). Now 5-8 of the 10 largest states keep their people and capital (before: 3-6), against 0-2 for a different
seed. But only 41-44% of ruled land keeps its ruling people (before: 21-38%; a different seed: 3%). The nudge is a +12.5% change to
one wish, and the peoples' shares move by under 4.2 points.

**What breaks if never done.** v3's nudge test ("the states are recognisably the same") and v4's done-when 5 stay borderline: the
biggest states mostly survive a nudge, but a map-wide comparison shows over half the ruled land changing rulers. A reader who
tweaks a preset sees borders redrawn across most of the map for a reason nobody can name.

**Try.** Split the remaining spread by step, with cheap re-derives on two stored runs (base and nudge; the derived steps take
under a minute each):
(a) hold the settlement ledger fixed (base's settlements.json under the nudge run) and see how much of the change is polities';
(b) compare the ledgers themselves: the share of towns and cities at the same cell with the same holder at 1,000 years ago and now;
(c) inside polities, check whether claim order (rank, incumbency) or the town threshold cascades a few changed seats into wide
border shifts. Then nudge the step that amplifies; don't tune constants to the check.
- [ ] the share of the change due to the ledger against polities, on 2 seeds
- [ ] the amplifying step named, with a candidate fix or a reason it is legitimate

## Updates
- 2026-11-04: Coordinator: v4, judged again once polities run inside the history (PW-1434); that changes how states form.
- 2026-11-04: Created from inbox draft draft-nudge-states-still-half-move.md (found by lane182).
