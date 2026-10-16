---
title: "Earth data: store Antarctica's and Greenland's true bed now that worlds take ice as land"
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: low
found_by: pw307-world-land
blocked_by: []
relates: [PW-307, PW-197]
refs: [tools/earth_data.py, tools/earth_world.py, planet/timezoom.py]
---

## Description
`tools/earth_data.py` floors the bed at 1 m wherever ETOPO1's bedrock is below sea level under ice
(West Antarctica, central Greenland) and thins the ice to keep the surface, because worlds used to
take land as elevation > 0. Since PW-307 worlds store the true bed and take grounded ice as land
(`geo.is_land`), so the Earth world (and Earth time zooms' start, `timezoom.source_earth`, which
notes the floored beds) could keep ETOPO1's bedrock. Ice shelves are counted as land there too
(land = ice surface > 0): a sample with a floating shelf should be sea with sea ice, not land ice
on a sunk bed; check what ETOPO1's ice-minus-bedrock gives for the shelves before changing it.
Needs the Earth cache rebuilt and the scorecard / earth_check re-run (Antarctica's climate should
not move: the surface is the same).
