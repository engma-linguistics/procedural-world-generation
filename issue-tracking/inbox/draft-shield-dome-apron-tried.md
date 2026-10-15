---
title: "Shield dome moats (PW-168): a pediment apron in the target doesn't help; domes also get striped by gullies"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-168]
refs: [planet/zoom_landforms.py, "world:a08983(-16.75,-28.53)"]
---

## Description
For PW-168 (merge into it). Tried on branch smalls2: `Shield.target` = 0.8 x max(dome, apron), the apron the same dome sites at 2x the radius with a lower, gentle profile (so the foot streams would run round a pediment). Compared hillshade crops of a 250 km, 0.5 km/px zoom at -16.75, -28.53 (world a08983) before and after: no visible change to the rings, and more domes came out striped by parallel gullies across their faces (the landscape pass incising the target's dome). Not taken. The stripes are a second artefact worth fixing with the moat: both suggest the landscape pass should not see the domes at all (mask the dome footprints out of the channel network and add the domes only in `shape`), and the drainage be deflected by a separate rule (route the streams round the footprints) instead of by the target.
