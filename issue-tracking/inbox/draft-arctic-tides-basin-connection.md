---
title: "Arctic tides still 2-5x too big: the Arctic basin counts as open ocean"
type: task
status: todo
parent: null
subsystem: coast
effort: s
impact: low
found_by: quickwins
blocked_by: []
relates: [PW-027]
refs: [planet/coast.py, tools/coast_check.py]
---

## Description
After PW-027's sea-ice friction, coast_check's Arctic tides are Laptev (Tiksi) 1.15 m (obs 0.1-0.6),
East Siberian (Kolyma) 1.43 m (0.1-0.4), Beaufort (Mackenzie) 3.10 m (0.2-0.6). Factors (connection,
shelf amp, funnel): Tiksi (0.63, 0.79, 1.15), Mackenzie (0.83, 1.63, 1.15). The connection is high
because the Arctic Ocean is wide enough to be "open ocean" in tide_range's openness test, but the real
Arctic is a near-enclosed basin fed only through Fram Strait and has a weak tide of its own (M2
amphidromes, ~0.1-0.3 m in the interior). The Mackenzie cell also sits on a shallow (20 m) cell at
quarter-wave resonance (W = 120 km).
Ideas: weight openness by the reach to *deep, large* ocean (an area or connectivity criterion rather
than a direction mean); or reduce the tide raised in a basin by its gateway width relative to its area.
Check the Mediterranean/Baltic/Gulf of Mexico rows in coast_check don't move.
