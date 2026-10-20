---
title: Emerging shelves and wet orogenic mountains are 40-60% of the cold-era weathering sink
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: pw438b
blocked_by: []
relates: [PW-438, PW-235]
refs: [planet/surface.py, planet/tectonics/earth.py, issue-tracking/tickets/PW-438-cold-eras-depth-is-not-set-by-the-climat.md]
---

## Description
In the cold eras of the PW-438 runs, newly emerged continental shelves (the sea-level fall exposes loose sediment on low ground) and wet orogenic mountains together carry 40-60% of the weathering sink. Since the base level no longer rises with the sea fall, the shelves are not planed faster, but they still erode as fresh land, so a lowstand adds to the CO2 sink just when CO2 should be rising. Cold eras also became more frequent after PW-438's change (time below -150 m up on seeds 3199 and 11: 19->31%, 18->37%), so this share needs a look: is it right physically (Earth's shelf weathering is real but small and slow), or does the erosion of emerging shelves (rate, sediment cover, `surface.erode` valley/alluvial terms) overcount it? Measure the sink by terrain class (shelf, orogen, craton) through a glacial and decide whether to exclude newly emerged ground for some Myr from the sink or to slow its erosion.\n- [ ] sink by terrain class in the cold eras of seeds 11, 2\n- [ ] decide and re-run the 4-seed table
