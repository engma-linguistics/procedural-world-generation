---
id: PW-642
title: "Resources: tin in melted collision belts rests on a crust-thinning proxy for exhumation; the run keeps the real record"
type: task
status: todo
parent: PW-155
milestone: v2
subsystem: surface
effort: s
impact: low
found_by: polish1
blocked_by: []
relates: [PW-616]
refs: [planet/resources.py, planet/tectonics/record.py, "zoom 439e2a", "zoom 72857c", docs/review/polish/polish-1.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-616's new Sn-W rule (polish1 lane) gives orogen basement its own S-type plutons in two cases:
- the history's collision crust melted (ramp 52-62 km);
- the crust has thinned 3-20 km since its peak (thick_max - thick).

That thinning stands in for exhumation. But the tectonics record already keeps the real erosion since a pluton
went quiet, as `record.EXHUMED` (crust.py uses it to expose granite at GRANITE_KM). It is not stored on
keyframes or worlds.

Storing it as a keyframe/world layer would give the roof-zone window directly: tin where 2-8 km have been
eroded off a melted belt. It would also serve gem_meta, whose "exhumed" is the same proxy. That would change
the run's outputs (a new layer), so it is a run-lane change.

Zoom 439e2a (31926a) sites 105 tin deposits (~30 notable) because its whole 500 km is a melted belt that lost
13 km, 24 Myr after its peak. With a real exhumation record, some of that ground might show its migmatite
root instead.
- [ ] Sn-W and gem_meta read a stored exhumation instead of the crust-thinning proxy

## Updates
- 2026-10-23: Created from inbox draft draft-snw-melted-belt-proxy.md (found by polish1).
