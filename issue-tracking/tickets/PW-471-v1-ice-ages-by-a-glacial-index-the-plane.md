---
id: PW-471
title: "V1 ice ages by a glacial index: the planet's orbit paces a scripted cold-warm curve, the time zoom's ice physics draws the sheets"
type: task
status: needs-decision
parent: PW-244
subsystem: timezoom
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-470, PW-440, PW-418, PW-037]
refs: [planet/timezoom/cycle.py, planet/timezoom/forcing.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
Owner 2026-10-20: park the ice-age physics (PW-470) and ship a faster, kludgier approximation for v1.

Proposal (coordinator lean): the glacial index method, a standard trick of ice-sheet modellers (e.g. Greve 1997, Marshall 2002). The modellers can't simulate what drives the cycles, so they script how cold it is and let the ice model work out where the ice goes.
- An index I(t) from 0 (interglacial) to 1 (glacial maximum) comes from a small conceptual model of global ice volume on the planet's own orbit. Use PW-440's three-mode cycle in cycle.py: slow growth (~80-90 kyr), a fast ending (~10 kyr) triggered by summer sun past a threshold, Huybers-style.
- The zoom's climate gets dT(t) = I(t) x the glacial cooling, polar-amplified, and the run's CO2 and ice-albedo feedbacks are switched off in the zoom.
  - The glacial cooling is planet-relative: a default ~5 C global for an Earth-like planet (LGM 4.5-6 C), scaled by how much land lies poleward of the planet's snowline. It can be set by hand.
- The existing ice physics (flow, margins, calving, isostasy) builds and melts the sheets, so the geography stays physical.
- The run is untouched: its 8/10 cold-era seeds stay as they are.
- The 25 m start-drift test is replaced by: the zoom's ice at I=0 is near the run's ice.

What this gives up: the cycle's timing and depth are scripted, not emergent.
What it gives: reliable ~100-kyr sawtooth cycles on any planet, sheets in plausible places, and bounded sea-level swings. That unblocks glacial carving (PW-037, PW-418 on branch pw037-carving) and the showcase remake (PW-202).

Options:
- (a) The glacial index as above. Lean. Effort m.
- (b) A target ice volume, with a controller pushing the melt boost until the ice follows it. The volume is guaranteed, but the geography is less physical and there's more tuning.
- (c) Skip ice-age cycles in v1: a finished world takes the run's ice plus one optional prescribed glacial maximum. Fastest, but no time zoom story.

Done when (a):
- Earth zoom: cycles of ~80-120 kyr with fast endings, glacial maxima -80 to -130 m, a Laurentide sheet south of 50 N at maximum, interglacial ice 9-12% of land.
- At least 7 of 10 run moments cycle, with no runaway: the sea level at each maximum is within 1.5x the planet-relative target.
- Run time no worse than today's.

## Updates
- 2026-10-20: Created.
