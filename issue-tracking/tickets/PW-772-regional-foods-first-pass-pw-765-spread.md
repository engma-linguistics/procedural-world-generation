---
id: PW-772
title: "Regional foods first pass (PW-765): spread restriction, viewer colours and what is still missing"
type: task
status: todo
parent: PW-692
milestone: later
subsystem: food
effort: s
impact: low
found_by: fun15
blocked_by: []
relates: [PW-765, PW-721, PW-738]
refs: [planet/lineages/crop_defs.py, viewer/index.html, planet/lineages/crops.py]
created: 2026-10-24
updated: 2026-11-03
---

## Description
PW-765 first pass added nine cuisine rows (weight 0, bits 24-32): nightshade fruits, squash, common beans, cacao, vanilla, peanut, sweet potato, quinoa/amaranth, avocado,
each with its own wild-range function, a slower spread front (0.4-0.7 against 0.9-1.5 for the staples) and an Earth anchor date. The crop layers `crop_wild` / `crop_known`
widened from uint32 to uint64 (33 rows; the viewer reads them as BigInt). Regional restriction comes only from the climate range, the landmass-drawn homelands and the slow
front; nothing cuts the sea or mountain barriers specially.
- [ ] Check the share of peopled land that knows each row on a few worlds (the front values 0.4-0.7 are guesses); tune only if they come out near-universal.
- [ ] Not yet in the pass: hot-pepper-like regional rows beyond chili, maize/potato-style staples stay as they are; no per-people taste of these foods.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: culinary follow-up of low weight; the core brief and cuisine tickets stay in v2
- 2026-10-24: Created from inbox draft draft-regional-foods-first-pass-followups.md (found by fun15).
