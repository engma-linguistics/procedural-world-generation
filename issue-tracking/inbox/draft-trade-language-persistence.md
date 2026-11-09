---
title: "Trade languages turn over every 650-800 years and are mostly a ruling state's tongue: should lingua francas be stickier?"
type: task
status: needs-decision
parent: null
milestone: v4
subsystem: peoples
effort: s
impact: low
found_by: lane-230
blocked_by: []
relates: [PW-1526]
refs: ["planet/lineages/tongues.py::pick", "planet/lineages/tongues.py::era_rows", docs/review/peoples/trade-languages.md, "runs 0141d1 3e0eb4 a24559 a2b637 07c755 3c1caf"]
---

## Description
In plain words: the new tongues ledger gives every long-haul trade network a trade language each era (0.5 kyr). On the six stored L7 runs
(4 dnd, 2 Seven Meals) a trade language lasts 1.3-1.6 eras on average (650-800 years), at most 5-11 eras, and 75-90% of network-eras take
the tongue of a state that rules peoples trading on the network; a merchant people's tongue or a pidgin is rare. History has lingua francas
that lasted far longer than the states behind them (Koine Greek for centuries after Alexander, Latin about 1,500 years after Rome, the
Mediterranean pidgin ~800 years; docs/review/peoples/trade-languages.md T§2, T§4). If nothing is done, a reader following one region sees
its trade language change every era or two, tracking whichever state holds the majority of its trade.

Why it churns: networks are traced afresh each era and matched to last era's by shared trading towns, and a new state carrying a majority
of the network's trade (RULE_TOWNS 0.5) beats an incumbent that is held at HELD 0.25 x INERTIA 2 = 0.5 at once.

Options:
- A. Keep as is: the turnover follows the run's polities, which also turn over by centuries.
- B. Stickier: raise INERTIA to 3 (a new tongue needs 75% of the network's trade to replace a stateless incumbent), or make HELD grow with
  the eras the tongue has served (an older lingua franca is harder to dislodge).
- C. Trade over rule: let a state's tongue win only where its own people also carry a large share (not just its subjects), so merchant
  peoples' tongues (Sogdian, Malay, Swahili) show up more.
Lean: B (one constant, cheap to check on the six runs: `tongues.ledger` takes 0.1-0.4 s per run once its era inputs are built, and
`tongues.frame_inputs` builds them in about 20 s to 2 min per L7 run from the cached exchange doc).
