---
title: One "sinking site" is the centroid of a sinking area from the Labrador Sea to the Barents
type: task
status: todo
parent: null
milestone: v2
subsystem: ocean
effort: s
impact: low
found_by: lane150
blocked_by: []
relates: [PW-1411]
refs: ["planet/ocean.py::overturning", tools/overturning_report.py, docs/review/base-climate/nordic-seas/round1.md]
---

## Description
In plain words: the report says the North Atlantic's water sinks in one spot off East Greenland. Really it sinks
over one large connected area, from the Labrador Sea to the Barents, and that spot is just the area's middle.

`overturning`'s `sites` are connected areas where sinking > 1e-3 Sv. On Earth L6 (main 65e13f48) the N Atlantic is
one area: 5.1 million km2, 12.55 Sv. Its centroid is at 67.3 N, 32.1 W. By basin (`nordmap.py`):
- Labrador, west of 45 W: 3.84 Sv;
- Irminger and Iceland basins: 2.92 Sv;
- north of the Greenland-Scotland ridge: 5.80 Sv.

PW-1411's "sinks off East Greenland" came from reading the centroid as a site. The viewer's loop schematic, and
anyone reading `moc_sites` or `overturning_report.py`, can be misled the same way.

- [ ] split `sites` into per-basin pieces (e.g. separate an area wherever the sinking per cell has a local minimum,
  or cut at sills shallower than LOOP_DEEP_M), or report the sinking by its strongest cells rather than the centroid
