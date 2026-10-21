---
id: PW-496
title: The glacial imprint is one time zoom deep, not an icehouse era deep
type: task
status: needs-decision
parent: PW-037
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: pw037
blocked_by: []
relates: [PW-037, PW-092, PW-104]
refs: [planet/timezoom/sim.py, planet/finish.py, docs/proposals/glacial_carving.md]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-037's carving runs only for the time zoom's span (300 kyr in the viewer, 1 Myr on the CLI). At
observed rates (Hallet's law, ~0.3 mm/yr at 80 m/yr of sliding) that leaves tens of metres under most
thawed ice and a few hundred metres in the fastest cells (Earth L6, 600 kyr on the glacial index,
2026-10-20: per Myr 15 m median, 128 m p90, 300 m p99 under the ice, so ~9 / 77 / 180 m in the zoom
itself). Earth's Great Lakes and fjords are the work of
~2.6 Myr and dozens of glaciations, so a finished world shows young-looking glacial landscapes at the
coarse scale. The main run's own ×3 glacial erosion (earth.py) does the long-term part, but without
basins, till or stripped cover.

Options:
- A. Leave it: the imprint is what this time zoom did (honest; the zoom, PW-092, makes the visible forms).
- B. Scale the finished world's imprint by the icehouse era's length from the run's record (Myr the cell
  was glaciated before the time zoom's moment, capped by the overdeepening bound the time zoom found).
  Approximation: past cycles repeat this one.
- C. Embedded ice ages in the main run (PW-104) carve as they go; the time zoom only adds the last Myr.

Lean: A now, C as the real fix; B is a cheap visual boost if the owner wants Great Lakes before PW-104.

## Updates
- 2026-10-21: Created from inbox draft draft-glacial-imprint-depth-only-one-myr.md (found by pw037).
