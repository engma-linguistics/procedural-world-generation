---
title: "Demes pass: 20-33 s per L7 run after the per-people cut; the next halving needs incremental re-cuts"
type: task
status: todo
parent: PW-981
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun46-demes
blocked_by: []
relates: [PW-981]
refs: [planet/lineages/demes.py, "run b69f51"]
---

## Description
In plain words: the demes pass that runs after each peoples run now takes 20-33 s on an L7 world (it took 71-134 s).
That is fine for now, but it is not "a few seconds". Cutting each people on its own cells helped less than hoped,
because together the peoples cover most of the land: on b69f51 their cells add up to 74,000-86,000 per frame,
1.3-1.45 times all the land (59,000 cells). So the pass still touches about the whole globe each frame.

Where the time goes now (b69f51, 129 frames, line profile on a loaded machine): the per-people cuts ~13-17 s (building
each local graph ~1.5 s, finding nearby cells ~1 s, the label Dijkstra ~1.5-2.3 s, diameters ~4.5 s), the corridor tags
~4.7 s (whole globe per frame), contacts ~2 s, reading the 112 MB world JSON for its rivers ~1.5 s.

Next steps, if it matters:
- re-cut a people only around the cells that changed since the last frame (most frames move a few percent of a range);
- compute the corridor cost on the union of the peoples' neighbourhoods, not the globe;
- keep the rivers (flow) in the run, so the pass need not parse the world JSON.
- [ ] demes.derive on b69f51 under 15 s, same output
