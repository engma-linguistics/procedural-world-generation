---
id: PW-133
title: Continental plume heads pile 7-16 km of flood basalt (Deccan ~2 km)
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: landform
blocked_by: []
relates: [PW-009]
refs: [planet/tectonics/volcanism.py, planet/tectonics/crust.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
At level 6 (seed 21, 500 Myr) the cover's lava column (`EXTRA` lava, now
the flood_basalt rock) reaches a median 0.5 km but 6.7 km at the 90th and
15.5 km at the 99th percentile; some cells carry 11-17 km of basalt strata.
Real continental flood basalts are 1-3.5 km thick (Deccan ~2 km, Siberian
~3.5 km, Columbia River ~1-2 km). The cause: `cap_plumes` lets the head build
until the ground stands at ~2000 m on a continent, and that height comes only
from isostasy of added crust (~150 m per km), so ~10+ km of lava is needed.
On Earth a plume head's high ground is mostly its dynamic swell (already
modelled as `lift`).

Try: cap the head's lava on continents by thickness (~3 km) or count the
swell in the height it builds toward, so the plateau stands high from the
swell and sinks as it decays. Check the lava_plateau class share and its
`strata_top_km` (landform.py) after.

## Updates
- 2026-10-14: Created from inbox draft draft-flood-basalt-too-thick.md (found by landform).
