---
id: PW-001
title: "Discrete volcanoes: hotspot and arc volcanoes as objects that ride their plate"
type: epic
status: done
parent: null
subsystem: tectonics
effort: xl
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [planet/tectonics/volcanism.py, planet/zoom.py, planet/world.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Today a hotspot is a continuous ~150 km Gaussian smear of crust (`volcanism.hotspots`, plume radius
150 km) and arc volcanoes are point objects (`volcanism.volcanoes`) that never leave the run. Make
volcanoes discrete objects end to end, so island chains, arcs and atolls appear in worlds and zooms.

- **Hotspots:** a new vent every ~50–100 km of plate motion over a plume, each a cone with its own
  height, subsiding with age (thermal subsidence) and eroding. At L7/L8 consecutive vents become
  separate islands (Hawaii–Emperor style), not a ridge.
- **Arcs:** the point objects in `planet/tectonics/volcanism.py` already exist; pass them on.
- **Worlds and zooms:** carry the volcano lists into worlds and zooms; the zoom draws separate cones,
  eroded older islands, and atolls once an island is old and in warm water.
- An Indonesia-like archipelago should fall out of arcs + a flooded shelf + microcontinents; use it as
  a showcase check.

Owner approved 2026-10-14 ("let's see it"), at level 7. Stories: run-side vents; world/zoom transfer;
zoom rendering (incl. atolls).

## Updates
- 2026-10-14: Status in-progress -> done. Done in worktree volcanoes (PW-002..004). Follow-ups filed as inbox drafts: coarse-grid islands (needs-decision), arc volcano density, continental calderas, zoom markers, chain highlights.
- 2026-10-14: Status todo -> in-progress. Started in worktree volcanoes (PW-002..004).
- 2026-10-14: Created from the 2026-10-14 discussion with the owner (approved, at level 7).
