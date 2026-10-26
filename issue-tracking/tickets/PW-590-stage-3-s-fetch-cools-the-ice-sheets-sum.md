---
id: PW-590
title: "Stage 3's fetch cools the ice sheets' summer air: Greenland ice warmest month -4.2 -> -6.6 C, Antarctic plateau +2.1 -> -0.4"
type: task
status: todo
parent: PW-570
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: base-climate-laneA12
blocked_by: []
relates: [PW-573, PW-336, PW-569]
refs: [planet/climate.py, docs/review/base-climate/laneA12/climate_bias_s3b.txt]
created: 2026-10-22
updated: 2026-10-23
---

## Description
Lane A12's fetch (`_summer_fetch`) applies to all land. It builds the summer air from the arriving sea air, weighted
by the land's share within `fetch_km`. The sheet's own share of the air (SUMMER_DAMP × damp_air) is kept out of it,
and that share stays the sheet's annual mean as before.

On Earth L6 (`laneA12/climate_bias_s3b.txt`, against `laneA10/climate_bias_e579.txt`):
- Greenland ice warmest month −8.4 → −10.8 (NCEP −4.2). It was already 4.2 C too cold, and is now 6.6 C too cold.
- Antarctic plateau −19.2 → −21.8 (NCEP −21.3), now right.
- Greenland rim (bare) +0.8 → +1.7.

Why: Greenland is ~1000 km wide, so its land share is ~0.6. The air is compared at sea level, so the sea air at ~0 C,
lifted 2 km, sits ~13 C under the sea-level summer the curve gives the sheet.

The sea air carried over a high sheet is arguably the right air above the sheet's own cold layer. But the sheet's
surface air is its own: katabatic, and held at or under 0 C by melt.

Options:
- A: keep it. It's the same rule as on bare land, and the Antarctic plateau improves.
- B: let the fetch act only on bare land, so a sheet keeps main's summer. Simple, but it treats a sheet as a big
  continent whatever its width.
- C: over a sheet, blend toward the arriving sea air only above the sheet's own boundary layer (the katabatic
  layer). Needs a sheet boundary-layer depth.

Lean: A for now. The time-zoom endings test passes with A (58 / 1.4 m; bar left < extra / 2), and the ice lane
(PW-569 / PW-439) owns the sheet's surface air.

## Updates
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-stage3-fetch-cools-ice-sheet-summers.md (found by base-climate-laneA12).
