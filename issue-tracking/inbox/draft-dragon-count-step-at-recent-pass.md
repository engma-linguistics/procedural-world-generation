---
title: "Dragons jump ~3.2x at 30 kyr ago (ice-age pass to recent pass): the empty land's food-fed density doubles at the hand-over"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977, PW-990]
refs: [docs/review/megafauna/dragon-density/index.html, docs/review/megafauna/dragon-density/numbers.json, planet/lineages/recent.py, planet/lineages/history/steps.py]
---

## Description
**In plain words.** The number of dragons on a world jumps about threefold in one step 30,000 years ago, exactly where the run switches
from its coarse ice-age pass to its finer recent pass. The jump comes from the empty land: across the switch its grazers feed about
twice as many dragons. With the peoples' pressure on, most dragons live on empty land, so the planet's count follows it; with the
pressure off it barely moves.

Evidence (review round 2, section 5.5; all runs, both arms; `numbers.json` `steps`, `step30_eras`):
- pressure on: x1.6 to x4.9 (median x3.2) between 30.0 and 29.9 kyr; pressure off: x1.2 median;
- nobody's country food-fed density 1.1 -> 2.2 per 1,000 km2 (31 -> 29 kyr; 1.2 -> 2.3 pressure off); its area 32% -> 36% of land;
- peopled country's food changes little (farmers' 18 -> 19).
Candidates: the ice-age pass's last step feeds a different climate or grazing NPP (ice, aridity) than the recent pass's first; the
prey field built from different fields in the two passes.
- [ ] compare grazing NPP on empty land at the ice-age pass's last step and the recent pass's first
- [ ] make the passes agree, or say why they differ
