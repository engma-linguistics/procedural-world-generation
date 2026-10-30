---
title: "Recent-pass droughts are hundreds of times rarer than Earth's and run long; add shorter, smaller, more frequent ones (and a viewer dial)"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lane-82
blocked_by: []
relates: [PW-917, PW-661]
refs: [planet/lineages/recent.py, docs/review/peoples-counterpressures/design.md]
---

## Description
**In plain words.** The climate model makes no droughts of its own. It is an average climate, computed every 2,000 years. The recent
pass's dice roll about two droughts per 30,000 years for the whole planet. A real region sees a drought decades to centuries long
every few hundred years: three in 500 years in the Mississippi Valley, two in California and Nevada, the 4.2 and 3.2 thousand-year
events in the Near East. Our droughts have Earth-like size and depth but are far too rare and somewhat too long. The owner's question
was whether the steppe could see droughts like those of PIE times. Today a given steppe gets one in the Holocene about once in 30
worlds.

Evidence and table: docs/review/peoples-counterpressures/design.md, section (a). Today's `RecentParams.episodes_per_kyr` = 1/6 (55%
cold spells); droughts last 0.2-0.8 kyr with radius 1,500-3,000 km and rain x0.5-0.75.

What to try (sizes from Cook & Seager's megadrought manuscript and Weiss 2016; rates are judgements to be screened):
- **Megadroughts.** A drought class of its own, at a rate that puts a given land cell in a drought core about once per 1-2 kyr (~15-20
  per kyr for an Earth-like planet).
  - Duration log-uniform 50-300 yr; radius 500-2,500 km; depth x0.5-0.8.
  - This means looping over the active episodes only: the cost now scales with every episode in the window.
- **Synchronous years.** Rare multi-cap events, a 4.2 ka-like one firing several caps at once, at ~1 per 5 kyr (judgement).
- **Old range.** Keep 300-800 yr only as the tail.
- **Viewer.** `meta.bad_years` (rare = today, Earth-like, harsh) as a viewer control. The owner uses the viewer, not the CLI.
- **Judging.** Count droughts per kyr per 2,000 km region from `Pass.episodes` (cheap, no history run). Then run the lane 77 suite
  arms today / Earth-like to see the peoples' response once the famine and habitat-tracking draft lands.

- [ ] drought class with Earth-like rate, duration and size; active-episode loop
- [ ] bad_years dial and viewer control
- [ ] episode statistics check against the design's table
