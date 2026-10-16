---
id: PW-361
title: Check an Earth time zoom's start on the true Antarctic bed
type: task
status: done
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: pw354-earth-bed
blocked_by: []
relates: [PW-354]
refs: [planet/timezoom.py, tools/earth_data.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Since PW-354 `timezoom.source_earth` gets ETOPO1's true bed (below the sea under 418 of 1003
Antarctic and 17 of 133 Greenland ice cells at L6, down to -1670 m) and no shelves (they are sea
in the data now), so its old shelf rule (thin ice on a floored bed -> sea at -500 m) is gone and
land is `geo.is_land`. Not run since: an Earth time zoom (e.g. 100 kyr at L6) should start with
its sheets grounded where the data has them (its flotation test, bed + H > sl + (1 - rho_i/rho_w) H,
may unground a few cell-mean grounding-line cells that the sample-level test kept), and its sea
level and ice volume (Antarctica ~24.8 million km3 of ice now, was 22.9 with the floored bed)
should start near today's.
- [ ] run an L6 Earth time zoom of ~100 kyr; compare its first frames' ice extent, volume and sea level with before

## Updates
- 2026-10-16: Status in-progress -> done. Partly done: true-bed start sane (1136 grounded ice cells, 25.15 Mkm3); calve_depth 1.5 -> 3 km (below Earth's deepest grounded beds ~2.5 km, above PW-199's ~4 km basins). West Antarctica's marine sector still retreats unforced in ~10 kyr: PW-367 (no shelves/ice streams).
- 2026-10-16: Checked (tzbatch). Earth L6 start on the true bed: all 1136 ice cells grounded (none fails the cell-mean flotation test), Antarctica 25.15 Mkm3, Greenland 2.85, sea level 0. Fixed: calve_depth 1500 to 3000 m (the 2 L6 / 9 L7 cells on beds 1.5-2.3 km deep under ~3 km of ice calved in place every step and unzipped West Antarctica from inside; L7 after 4 kyr: Antarctica -0.7 m SLE before, +0.1 after). Not fixed (draft draft-timezoom-marine-margins.md, needs-decision): unforced (orbit held), West Antarctica's whole marine sector still retreats in ~10 kyr (95 cells, 2.3 Mkm3, -3.8 m SLE above flotation): no shelves or ice streams; Greenland's region grows +2.3 m (cold bias, PW-114/PW-033), so sea level stays near 0 by cancellation. Default 1 Myr Earth zoom: sea level -15..+14 m, Antarctica ~22.1 Mkm3 after the first 10 kyr, Greenland flips between 0 and 3.8 Mkm3 with precession (PW-114). Write-up docs/review/timezoom/batch-2026-10-16.md.
- 2026-10-16: Status todo -> in-progress. Time zoom batch agent started.
- 2026-10-16: Created from inbox draft draft-earth-timezoom-true-bed.md (found by pw354-earth-bed).
