---
id: PW-1171
title: Recent-pass droughts are hundreds of times rarer than Earth's and run long; add shorter, smaller, more frequent ones (and a viewer dial)
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: lane-82
blocked_by: []
relates: [PW-917, PW-661]
refs: [planet/lineages/recent.py, docs/review/peoples-counterpressures/design.md, planet/climate.py, docs/review/peoples-events/design.md]
created: 2026-10-30
updated: 2026-11-03
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

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: war, plague, events and life-history belong with the v3 civilization epic (PW-661); not needed for a first culinary brief
- 2026-10-31: Merged inbox draft draft-droughts-from-climate-variability-physics.md ("Droughts from the climate's own variability: Earth-like megadrought rate, placed where the model's rain is touchy (v2 physics)", found by lane-85).
  **In plain words.** The climate model has no droughts of its own. It is an average climate, computed every 2,000 years. The few droughts
  the peoples ever see are dice rolled by the recent pass. There are far too few, and they land anywhere on land, not where real droughts
  happen (semi-arid margins, monsoon edges, the westerlies' fringe). Real regions get a drought decades to centuries long every few
  hundred years. Ours get one hundreds to thousands of times less often. The owner's example is the steppe droughts of Indo-European
  times: a given steppe gets one in our Holocene about once in 30 worlds.
  
  **The numbers.**
  - **Ours** (`RecentParams.episodes_per_kyr` = 1/6, 45% droughts, 0.2–0.8 kyr, radius 1,500–3,000 km, rain ×0.5–0.75 at the centre).
    That's 0.075 droughts per kyr for the whole planet, ~2.25 per 30 kyr window.
    - A given land cell is in some drought's cap ~0.6% of the time, and in its half-strength core ~0.15%. Our arithmetic: 0.075/kyr ×
      0.5 kyr mean × a cap of ~16.5 Mkm² mean area over ~100 Mkm² of land within 50°.
    - By count, a cell sits in a core about once per 330 kyr (lane 82).
  - **Earth.**
    - California–Nevada was in megadrought 862–1074 and 1122–1299 CE, 389 of the Common Era's ~2,000 years, ~19% (Cook et al. 2016,
      *WIREs Clim Change* doi:10.1002/wcc.394, read; share our arithmetic).
    - The 4.2 ka megadrought lasted "200-300 year" with an "estimated 30-50% reduction in precipitation" (Weiss 2016, *PAGES Mag.*
      24:62, read).
    - A region sees one every ~150–500 yr (lane 82's table).
  - **The gap.** 30× (any cap) to 125× (core) in time spent in drought; 100–1,000× by count (lane 82). Duration: ours 200–800 yr
    against 10–300.
  
  **What physics says.** Cook et al. 2016: models make megadroughts "through (1) internal atmospheric variability, (2) sea-surface
  temperatures, and (3) land surface and dust aerosol feedbacks", and "their persistence suggests a role for processes that impart memory
  to the climate system (land surface and ocean dynamics)". So chance is the right base, but the place and the persistence should come
  from the climate:
  - **Sensitivity map, once per recent pass.** `climate.compute` perturbed by a few ocean-basin SST anomaly patches (one per basin and
    sign), cached like `recent_rain.npz`. This gives dP/dSST per basin on every cell.
  - **Basin modes.** A red-noise SST index per basin, with decadal memory (judgement tau 20–60 yr). Rain anomaly = Σ index × sensitivity.
  - **Land memory.** A soil-moisture AR(1) with decades of memory, amplifying dry anomalies on semi-arid cells.
  - **Episodes from the anomaly.** A drought episode is where the smoothed anomaly stays below −25% for ≥ 10 yr (Cook: "durations longer
    than a decade"). They enter the existing `Episode` list, so the history, the settlements and the stored frames agree, as today.
  - **Calibrate.** One knob, the index amplitude. On an Earth-like world, a ~2,000 km region should spend ~5–20% of its time in
    megadrought (a target from the California–Nevada figure, judgement on the spread), with durations of 10–300 yr.
  - **Cost.** A handful of extra `climate.compute` calls per recent pass (minutes at L7, cached once).
  
  **Relation to PW-1171.** PW-1171 retunes the dice (rate, size, length, a `bad_years` dial). This ticket keeps the dice but places
  and paces them physically. The coordinator may merge the two (`--merge-into PW-1171`); the lean is to keep PW-1171's `bad_years`
  dial as the knob this one drives.
  
  - [ ] basin sensitivity map, cached
  - [ ] basin red-noise indices + soil memory, giving Episodes
  - [ ] drought statistics per 2,000 km region, against the targets above, on the showcase worlds (no history needed)
  - [ ] diagnosis written first (diagnosis gate), then the screen
- 2026-10-30: Created from inbox draft draft-recent-droughts-earthlike-rate.md (found by lane-82).
