---
title: "Atoll group highlight chains whole oceans together (124 atolls 'within ~7,400 km')"
type: task
status: todo
parent: null
subsystem: highlights
effort: xs
impact: low
found_by: volcano-highlights
blocked_by: []
relates: [PW-119]
refs: [planet/highlights.py, "run a1d3b9"]
---

## Description
`highlights.atolls` groups atolls by single linkage within ATOLL_LINK_KM (300 km). On a world sliced from run a1d3b9 (L7,
seed 3199 @ 380 Myr; a world with many atolls) that chains 124 atolls and 45 reef islands into one
"group" spanning ~7,400 km, so the blurb reads "124 coral atolls ... within ~7,400 km". The zoom is fine
(`_best_window` picks the densest 350 km), but the count and extent describe an ocean, not a group like
the Tuamotus (~1,500 km). Try: count and measure only the atolls within the zoom window (or within
~1,000 km of its centre), and say how many more lie beyond.
- [ ] the atoll blurb's numbers describe what the zoom shows
