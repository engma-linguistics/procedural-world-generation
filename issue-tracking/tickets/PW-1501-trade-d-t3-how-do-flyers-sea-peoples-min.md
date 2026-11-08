---
id: PW-1501
title: "Trade D-T3: how do flyers, sea peoples, mining kinds and dragons carry and trade goods?"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: xs
impact: med
found_by: lane 211
blocked_by: []
relates: [PW-1491, PW-1494]
refs: [docs/review/culture/trade/design1.md, docs/review/culture/trade/review1.md, planet/lineages/polities.py, planet/lineages/spec.py, "planet/lineages/land.py::SEA_GOODS"]
created: 2026-11-07
updated: 2026-11-07
---

## Description
In plain words: every real-world source in the review is about humans walking, riding, rowing and sailing. The model's peoples
also include:
- flying kinds;
- sea peoples who live under water;
- mining kinds in halls;
- dragons, who are sapient and take tribute.

The cost graph (step 2) needs a rule for how each of these carries goods.

Options:
- A. The body plan sets the carrier:
  - flyers pay a flat cost per km over any ground, mountain or sea, but carry only light, precious goods (no grain cargo);
  - sea peoples move goods over the shelf as cheaply as boats do, and trade with land peoples only at shores;
  - mining kinds trade from their holds as towns do;
  - dragons take tribute from the settled land around them (polities already seats dragon realms) and do not trade.
- B. As A, but dragons also trade: gems and gold from their hoards go out, and cattle and gold come in. This makes dragon realms
  trading hubs.
- C. No special carriers in the first version of trade. Everyone moves goods the human way, and the fantasy kinds differ only in
  what their land yields.

Trade-offs:
- A uses only traits the tree already has (flyer, swimmer, miner), and keeps the sapient dragons as rulers, as ruling O4 framed
  them.
- B is more colourful, but it needs a rule for what dragons want, and nobody has sourced one.
- C is simplest, but flyers would be blocked by mountains they fly over.

**My lean: A.** If this is never decided, step 2 treats flyers and sea peoples like walkers, and the brief will show merfolk
buying salt over land.

## Updates
- 2026-11-07: Created from inbox draft draft-trade-d3-fantasy-carriers.md (found by lane 211).
