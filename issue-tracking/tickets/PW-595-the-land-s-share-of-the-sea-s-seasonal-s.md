---
id: PW-595
title: "The land's share of the sea's seasonal swing (_sea_half) is a big continent's swing, whatever the land's width: off Patagonia the sea's half-swing is 6.2 C against 3.7"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: ocean
effort: s
impact: med
found_by: base-climate-laneA14
blocked_by: []
relates: [PW-593, PW-573]
refs: [planet/climate.py, docs/review/base-climate/laneA14/p3_attempt1.txt, docs/review/base-climate/laneA14/pw593_attempt1_toggles.diff]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`_sea_half` adds `c x continental x s x land_air` to the sea's own swing, where the air over the sea came off
land. `continental x s` is the swing of a big continent. Stage 3's `_summer_fetch` (PW-573) already says narrow land
in a westerly gives only part of that swing: the boundary layer's share `sum_h / fetch_h`, plus the rest times the
land's share within `fetch_km`. The sea's land part ignores that, so the seas off Patagonia, S Africa and Tasmania
take on a continent's swing. Off Patagonia, `sea_half` is 5.7 C, of which ~3.5 is the land part. The sea's
half-swing is 6.2 against NCEP's 3.7.

Lane A14 measured weighting the carried land by that same fetch share (`land_fetch=1` in the saved diff;
Earth L6, `laneA14/p3_attempt1.txt`):
- SH: coastal range 12.4 → 11.6, SH near-land sea swing within 1.5x 54 → 66%, Patagonia's sea swing 6.2 → 4.9,
  NZ warmest +1.1 → +0.4, Tasmania +6.0 → +5.5.
- But NH: near-land swing within 1.5x 52 → 43%, the North Sea / Biscay's summer −2.4 → −3.7, W Europe −1.2 → −1.9.
- Rain r 0.620 → **0.613** (bar ≥ 0.617).

It is sounder (the sea gets the land air the fetch actually makes), but it cools Europe's seas, whose swing was
right only because the NE Atlantic's own swing is too small (PW-593). Not merged. It belongs with PW-593's layer,
once the winds allow that (see the draft on the summer mixed layer and the seasonal winds).
- [ ] the land part of the sea's swing from the fetched land air, merged together with a summer layer that restores
      the NE Atlantic's own swing; rain r ≥ 0.617

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Created from inbox draft draft-sea-swing-land-part-is-a-big-continents.md (found by base-climate-laneA14).
