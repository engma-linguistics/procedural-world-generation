---
id: PW-746
title: "Salt distance looks too long (mean ~800-900 km, tundra ~1500 km): check inland sources (salt licks, saline springs, plant ash, playas) against real interiors"
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-732]
refs: []
created: 2026-10-24
updated: 2026-10-24
---

## Description
fun9's salt goods give a mean land distance to salt of 885 km (1df1c3) and 763 km (3e9e7d), 88-93% of subarctic/tundra beyond 300 km. Real interiors had many small sources: saline springs and licks over sedimentary basins, playas in dry country, plant-ash salt (central Africa, New Guinea), animal licks herders follow. Check the inland source rules against a few real interiors (Earth world 506694: Sahel, Great Plains, Siberia, Amazon) before the brief reads salt scarcity as a driver.

## Updates
- 2026-10-24: Status todo -> done. Merged 5a105aa: playas, basin brines, licks; Earth mean 1028->304 km. Real-geology check is PW-747.
- 2026-10-24: Built on branch fun10 (seafood.py): playas (closed dry drainage ends), brine springs over any sedimentary basin, mineral licks (rivers over shale, tuff, coal, evaporite); plant ash stays a marker (not a distance source). Mean land distance to salt: Earth 506694 1028 -> 304 km, 1df1c3 885 -> 332, 3e9e7d 763 -> 329; regions in docs/proposals/lineages.md. Tundra stays the farthest (Earth 422 km): inland arctic peoples got salt from meat and blood, not a source.
- 2026-10-24: Created.
