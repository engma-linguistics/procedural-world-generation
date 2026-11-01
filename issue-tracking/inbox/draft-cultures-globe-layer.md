---
title: "Emergent cultures: a globe layer coloured by culture (today the Cultures tab's map link opens the demes layer)"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: lane107
blocked_by: []
relates: [PW-670, PW-981]
refs: [viewer/lineages.html, viewer/globe/layers.js, viewer/globe/colours.js, planet/lineages/cultures.py]
---

## Description
In plain words: the Cultures tab's "map" link opens the globe on the regional-populations (demes) layer, centred on the
culture. You see the culture's land, but split into its demes and coloured by them. A "cultures" layer would colour each
cell by its culture instead. No new data is needed: cultures.json has `deme_culture` (deme -> culture) and each culture's
`end`, `into` and `ended_kyr` for merges. The layer maps `layers/demes.bin` through that, resolving merges at the frame's
time, and takes the colours from cultures.json. For runs without the file, load it from `/api/cultures`.
- [ ] globe layer 'cultures' under peoples, legend of the largest cultures in view
- [ ] the Cultures tab's map link opens it
