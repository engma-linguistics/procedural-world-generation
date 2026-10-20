---
id: PW-030
title: "Time zoom: no real 100-kyr sawtooth"
type: task
status: todo
parent: null
subsystem: timezoom
effort: l
impact: high
found_by: timezoom
blocked_by: [PW-366]
relates: [PW-018, PW-037]
refs: [planet/timezoom.py]
created: 2026-10-14
updated: 2026-10-19
---

## Description
Ice shrinks back 20–50 m (sea-level equivalent) at insolation peaks, but the trend ratchets upward;
there are no terminations. They need mechanisms not modelled yet: a CO₂ rise independent of the ice,
proglacial lakes, dust darkening the ice, and the overturning/meltwater coupling (PW-018).

## Updates
- 2026-10-19: Status blocked -> todo. Unblocked by PW-366 (2026-10-19). PW-436 (forced zoom from cold moments only loses ice) and PW-435 (Earth's glacial shallower, -33 m) fold into this work.
- 2026-10-16: Status todo -> blocked. Owner decision 2026-10-16 late night: real ice-age cycles (slow ~80-90 kyr builds, fast terminations, swing >= 80 m) ARE in v1. Impact high; blocked in practice on PW-366 (follows it in the run lane).
- 2026-10-16: Evidence (2026-10-16 night, read-only analysis of time zooms 98ee98, 080df3, 86c513; images in the coordinator's scratchpad iceq/): the upward ratchet in this ticket's text is gone. Cold moments now heartbeat. After the fast start (PW-241/295) sea level holds a plateau with melt spikes at precession peaks: melt takes ~12 kyr and regrowth 10-34 kyr. Swings are 15-72 m (median ~39 m; the 5-95% band is 51 m), against Earth's 120-130 m. The spectra peak at 100 kyr only by rectification: eccentricity clusters the spikes. There are no long builds and no terminations. The cycling ice is margin lobes on sheets that never go away (interglacials still ice 17-25% of land; Earth today ~10%). Extent at maximum is fine (26-34% of land; margins reach 31-40 degrees). Owner (2026-10-16): wants ice ages that visibly ramp up and end, not a heartbeat. Acceptance metric proposal: swing >= 80 m with 80-90 kyr builds and ~10 kyr terminations from a moderately cold moment. Do this before or alongside PW-104, so the run doesn't inherit heartbeat cycles. Blocked in practice on PW-366 (the time zoom's start drift).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom.
