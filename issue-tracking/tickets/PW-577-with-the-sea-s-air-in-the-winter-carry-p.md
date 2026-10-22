---
id: PW-577
title: With the sea's air in the winter carry, PW-575's offshore Nordic winds chill the open Norwegian Sea (air -4.4 vs +3.5 C), and Baffin Bay's summer runs +8.7 C
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: med
found_by: base-climate-laneA2
blocked_by: []
relates: [PW-575, PW-346, PW-458]
refs: [planet/climate.py, docs/review/base-climate/stage2/attempt2.patch, docs/review/base-climate/stages.md, tools/climate_bias.py]
created: 2026-10-22
updated: 2026-10-22
---

## Description
Found in lane A stage 2's attempt 2 (`docs/review/base-climate/stage2/attempt2.patch`, Earth L6). These are two side
effects for whoever lands the sea's air in the carry (see `draft-sea-swing-from-land-air-vs-rain.md`).

1. **The Nordic Seas.**
   - On main the sea's air is pinned to its water, so the open Norwegian Sea's winter air is +0.6 C.
   - Once the sea's air takes part in the carry, the winter wind there blows offshore (north-easterly, PW-575). It
     brings the land's and the Barents ice's cold over the open water.
   - The water stays open (100%, SST +1.5 C), but its air goes to −4.4 C (NCEP ~+3.5). The Nordic Seas box falls to
     −10.4 against −1.8 (main −4.7), and the Barents Sea to −24.5 against −10.8.
   - Fennoscandia still improves a little (−14.7 → −12.2), because Hudson Bay and the Arctic change upstream.
   - This makes PW-575's wind fix (winds from the full sea surface, or the storms' eddy heat) a prerequisite rather
     than an option.
2. **Baffin Bay's summer.**
   - With the swing from the land's air, Baffin Bay's swing is large.
   - `ocean.winter_half` damps its winter (the overturning's inflow layer) but not its summer, so its summer sea
     air is +10.3 C (NCEP +1.6). The Labrador Sea / Baffin box gets +6.7.
   - The summer's warming over a deep inflow layer, or the summer melt of the pack beside Baffin Island, should hold
     it near 0–3 C.

- [ ] Norwegian Sea winter air within ~3 C of NCEP with the sea's air in the carry
- [ ] Baffin Bay's warmest month within 3 C

## Updates
- 2026-10-22: Created from inbox draft draft-sea-air-carry-offshore-and-baffin-summer.md (found by base-climate-laneA2).
