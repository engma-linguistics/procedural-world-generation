---
title: Show the den ground (caves, rock shelters, ground to dig) as a viewer layer
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: lane 143
blocked_by: []
relates: [PW-1382]
refs: [planet/lineages/dens.py, "planet/lineages/dens.py::fitness", "planet/lineages/land.py::_make_goods", "planet/lineages/ladder.py::den_thin", viewer/lineages.html, docs/review/peoples/dens/round1.md]
---

## Description
In plain words: the peoples now read a "den ground" map (0 to 1 per cell: karst and other limestone, lava plains, tuff, rock
shelters in cliffed hard rock, sea cliffs, thick loess and deep soft soil; PW-1382, lane 143), and den peoples (kobolds, goblins)
live up to twice as densely on the best of it. Nobody can see that map yet: the land goods are not a viewer layer, so Daniel cannot
check where the caves are or why kobolds cluster where they do.

What to do: expose the `den` good (land.goods(world)["den"]) as a layer in the lineages workbench (or the world tab), a single-hue
ramp 0..1, with a tooltip naming the best den kind in the cell (karst, lava tubes, carved tuff, rock shelters, sea caves, loess,
soil). dens.fitness would need to return which part won (an argmax) for the tooltip.
- [ ] a den-ground layer the owner can toggle in the viewer
- [ ] the tooltip names what kind of den ground the cell has
