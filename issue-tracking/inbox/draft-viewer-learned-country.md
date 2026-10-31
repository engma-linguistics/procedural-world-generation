---
title: "Viewer: show learned country and adapted demes (niche learning)"
type: task
status: todo
parent: PW-917
milestone: v1
subsystem: viewer
effort: s
impact: med
found_by: lane79
blocked_by: []
relates: [PW-1155, PW-981]
refs: [planet/lineages/output.py, planet/lineages/demes.py, planet/lineages/history/frame.py]
---

## In plain words
Peoples can now slowly learn to live in new country: tundra elves, desert aarakocra, plains gnomes. The run stores where that has
happened, but the viewer cannot show it yet. You use the viewer, not the command line, so this needs a control there.

## Description
Niche learning (PW-1155) writes the following:
- a per-frame layer `peoples_learned`: the leading people's learned acceptance of the cell, in %. It is 0 on the people's own
  country and 100 where it is fully at home up to its body limits;
- `stats.learned` per frame: Mkm² of learned country per line, by biome class (habitat.BIOMES);
- in demes.json, `adapted` and `learned_share` per deme, plus a new event kind `split_adapted` ("took to new country apart from X").

Wanted in the viewer:
- the layer as a peoples overlay, e.g. a hatch or tint over the peoples map where learned >= 50%;
- deme labels that show "adapted: tundra" in the demes panel;
- the `split_adapted` events in the deme timeline.
