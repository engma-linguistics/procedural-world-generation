---
id: PW-197
title: "Finished worlds: grounded marine ice is stored as land with the bed floored at 1 m"
type: task
status: done
parent: PW-090
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: finish
blocked_by: []
relates: [PW-091, PW-189]
refs: [planet/finish.py, tools/earth_data.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
The world format has no "grounded ice on a bed below sea level": land is elevation > 0. So
finish.py floors the bed of such cells (marine ice sheets, and beds pressed below the sea by
thick ice) at 1 m and thins the ice to keep the surface, as tools/earth_data.py does for
Antarctica. The bed shown under those cells is wrong (zooms, rock, a "lake" under the ice can't
appear); the surface is right. meta.marine_ice_floored_cells counts them. A proper fix stores the bed as is and lets world/climate/hydrology treat
"ice-covered, bed below sea level" as land (ties to PW-189 glacial isostasy).

## Updates
- 2026-10-16: Status in-progress -> done. Done with PW-307 (e4c341a): finished worlds store the true bed of grounded marine ice.
- 2026-10-16: Status todo -> in-progress. With PW-307.
- 2026-10-15: Status in-progress -> todo. Bigger than estimated: the 1 m bed floor is applied in timeline._world for every world; the real scope (world-wide land = bed > 0 or grounded ice) is PW-307.
- 2026-10-15: Status todo -> in-progress. Agent started (small-ticket batch, 2026-10-15).
- 2026-10-15: Ice: runs and time-zoom frames store the true bed; worlds still floor at 1 m (no world bed layer yet).
- 2026-10-14: Created from inbox draft draft-finish-marine-ice.md (found by finish).
