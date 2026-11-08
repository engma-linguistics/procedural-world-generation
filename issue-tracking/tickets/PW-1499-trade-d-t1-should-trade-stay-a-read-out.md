---
id: PW-1499
title: "Trade D-T1: should trade stay a read-out after the run, or feed back into the history (densities, dwarven holds, foragers)?"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 211
blocked_by: []
relates: [PW-1371, PW-1405, PW-1406, PW-661]
refs: [docs/review/culture/trade/design1.md, docs/review/culture/trade/review1.md, "planet/lineages/ladder.py::TRADE_CAP", "planet/lineages/ladder.py::BARTER_CAP", "planet/lineages/salt_reach.py::_spfa", planet/lineages/output.py, planet/lineages/polities.py]
created: 2026-11-07
updated: 2026-11-07
---

## Description
In plain words: the trade design (design1.md) works out what each culture has and lacks, how goods move between neighbours
and along which roads. The question is whether this stays a picture painted after the run, like the towns and the polities,
or whether the run uses it while it runs. If it does, a people fed by bought grain grows denser and spreads further.

Two pieces of the run already pretend trade exists. Dwarven holds buy up to half their food (`ladder.TRADE_CAP`, a placeholder).
Forager peoples get up to half their food from farming neighbours (`ladder.BARTER_CAP`: the cap is sourced, the shape is a
judgement). If trade never feeds back, both stay placeholders.

Options:
- A. Read-out only, for steps 1 to 4c: goods, exchange, routes, the culinary brief, tech and faith spread, and polity wealth.
  Revisit feedback once the routes look right on several trees.
- B. Read-out first, then feed only the food flows back into the two placeholders (holds and foragers). The history would compute
  the food part of step 2 every frame.
- C. Full feedback: trade flows change carrying capacity everywhere during the run (cities fed from afar, herders fed by grain).

Trade-offs:
- A is cheap and can't destabilise the history. Read-outs re-run in minutes; a history re-run costs hours.
- B replaces two named placeholders with a mechanism. But it makes the history slower, and every trade change then needs a full
  re-run.
- C is the most realistic (Rome ate Egyptian grain: review1.md section 4) and the most fragile: a nudge to one route could move
  peoples' ranges.

**My lean: A now, then B as the last step (4d), once steps 1-3 are judged on the stress trees.** If this is never decided, the two
placeholders stay, and the brief's bought-in foods won't match the densities the history gave.

## Updates
- 2026-11-07: Created from inbox draft draft-trade-d1-readout-or-feedback.md (found by lane 211).
