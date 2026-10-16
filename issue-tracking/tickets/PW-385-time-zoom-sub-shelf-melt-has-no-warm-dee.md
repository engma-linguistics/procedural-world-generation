---
id: PW-385
title: "Time zoom: sub-shelf melt has no warm deep water to work with (Antarctica's shelves go only by the air)"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: low
found_by: pw367-buttress
blocked_by: []
relates: [PW-367]
refs: [planet/timezoom.py, planet/ocean.py, docs/overview.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Since PW-367 the time zoom's ice shelves melt from below at `melt_k` = 10 m/yr per °C of the water under
them above freezing. The rule is in place, but around Antarctica it never acts.

**Why:** the model's ocean has only a surface temperature, so the water under a shelf is taken to be the
sea's winter surface water (`min(sst_jul, sst_jan)` from `climate.compute`). Earth L6's winter water
beside Antarctica stays at −1.8 °C, the freezing point, at dT 0, +2, +4 and even +6 °C.

**Effect:** a warm start loses West Antarctica only because the air over its seas warms past −5 °C and the
shelves break up (+4 °C: 91/149 marine cells at 20 kyr, 53 at 50 kyr). In reality the Amundsen sector's
retreat, today and probably in the Eemian, comes from warm Circumpolar Deep Water (~+1 °C, ~3 °C above the
freezing point at depth) melting the shelves from below.

**What to try:** give the time zoom a subsurface water temperature for the shelf seas. Two possible sources:
- the overturning's inflow temperature (`ocean.solve`);
- a latitude profile of deep water with the global dT.

Either belongs to the ocean lane, so this waits for its rain rework to settle.
- [ ] a warm Eemian-like Earth start melts the Amundsen sector's shelves from below (melt > 1 m/yr) and
      today's climate doesn't

## Updates
- 2026-10-16: Created from inbox draft draft-timezoom-shelf-ocean-heat.md (found by pw367-buttress).
