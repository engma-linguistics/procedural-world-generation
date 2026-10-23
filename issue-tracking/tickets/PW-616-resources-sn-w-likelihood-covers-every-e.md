---
id: PW-616
title: "Resources: Sn-W likelihood covers every exhumed granite, so zooms fill with tin deposits"
type: task
status: done
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
- 2026-10-23: Status todo -> done. Merged (44c50c9): Sn-W from collision-thickened crustal melts with a fading roof zone; >=0.5 likelihood 4-5% -> 0.05-0.24% of land. Run exhumation record: PW-642.
- 2026-10-23: polish1 lane (branch worktree-agent-ab67a9e26ffa4d792): Sn-W by mechanism. The history records collision crust (coll_thick) and continuous granite exposure (granite_myr). Tin granites = granite x (0.04 + 0.86 x S-type) x roof, where S-type = ramp(coll_thick, 52, 62) x reduced source, and roof = exp(-granite_myr/150). Melted collision belts get 0.4 x S-type x an exhumation window (3-20 km of crust lost) x 10-30 Myr incubation. sn_w >= 0.5 now covers 6-23% of granite cells, and 0.05-0.24% of land instead of 4-5%. Zoom 72857c: 286 -> 0 deposits (a plateau still thickening). Zoom 439e2a: 331 -> 105, ~30 notable (a genuinely melted belt). docs/review/polish/polish-1.md. Follow-up draft: draft-snw-melted-belt-proxy.
- 2026-10-23: Created from inbox draft draft-resources-snw-granite-spread.md (found by resources2).
