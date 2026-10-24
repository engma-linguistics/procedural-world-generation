---
id: PW-622
title: "Zoom barrier islands as terrain: opt-in add-on (--terrain) or a step of planet zoom?"
type: task
status: done
parent: PW-097
milestone: v2
subsystem: zoom
effort: m
impact: med
found_by: coast-detail
blocked_by: []
relates: [PW-097, PW-326]
refs: [planet/zoom_coast.py, planet/zoom.py, "zoom ccf03a (scratch store)", docs/review/coast_detail/]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`planet coast zoom:<id>` draws barrier islands, lagoons and tidal inlets as a layer (barrier_island), and
with `--terrain` raises the islands 1.5-3 m out of the sea (elevation and water rewritten in place). Opt-in,
so existing zooms and the zoom goldens are untouched. But the terrain step runs after the zoom's rivers,
satellite view, coastal life and harbours, which then don't see the islands (rivers still end at the old
shore, the satellite shows sea, harbours don't know the lagoons are sheltered).
- A: keep it opt-in and after the fact (built).
- B: make it a step of `planet zoom` before rivers/satellite/coastal life (zoom goldens move; owner OK needed).
Lean: B, with the lagoon as sheltered water for humanuse and the inlets as hazards, after the owner has seen
docs/review/coast_detail/zoom_ccf03a_barrier.png.
- [ ] islands in zoom.py before the landscape pass; rivers reach the lagoon; satellite sand colour
- [ ] lagoons count as sheltered water in humanuse harbours

## Updates
- 2026-10-23: Status todo -> done. fun5: B built. zoom.build makes the barrier islands (zoom_coast.islands, 1.5-3 m) in the coastline step, before rivers, vegetation, coastal life, harbours and the satellite view; planet zoom then runs the coast layers. Lagoons shelter harbours through the fetch but are too shallow to rate (draft-lagoon-harbour-depth); spits are still after the fact (draft-zoom-shore-forms-in-build).
- 2026-10-23: Status needs-decision -> todo. Owner (2026-10-24): B: barrier islands as a step of planet zoom before rivers, satellite, coastal life and harbours (zoom goldens move, OK'd).
- 2026-10-23: Created from inbox draft draft-zoom-barrier-terrain.md (found by coast-detail).
