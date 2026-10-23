---
id: PW-616
title: "Resources: Sn-W likelihood covers every exhumed granite, so zooms fill with tin deposits"
type: task
status: todo
parent: PW-155
milestone: v2
subsystem: zoom
effort: s
impact: low
found_by: resources2
blocked_by: []
relates: [PW-155, PW-610]
refs: [planet/resources.py, planet/zoom_resources.py, "zoom 72857c", "zoom 439e2a"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Stage 1's sn_w rule gives 0.55 to any exhumed granite cell (x1.4 where the crust was once > 50 km), so wide
granite terranes become one big tin district. Stage 2's siting reads a likelihood as P(a notable deposit in the
cell), so the zooms get hundreds of tin-tungsten deposits in 500 km: 72857c (L7 1144ce) has 286 and 439e2a
(L7 31926a) has 331, against 5-50 for every other metal. Real tin provinces are a minority of granites: the
S-type (crustal-melt) granites of thick collision crust, and only their roof zones.
Fix it by mechanism: make granite x the thick-crust history (thick_max >= 50-55 km within the granite's age)
the main term, and give I-type arc granites (arc rock, no thick crust) much less, since they carry porphyry Cu
instead.
- [ ] sn_w at >= 0.5 covers a minority of granite cells on the four check worlds; zooms 72857c and 439e2a
      site tens of deposits, not hundreds

## Updates
- 2026-10-23: Created from inbox draft draft-resources-snw-granite-spread.md (found by resources2).
