---
id: PW-538
title: The glacial cooling scales with ice-free snowline land, so a run moment with its ice already down gets almost none
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: worktree-agent-a1bb68a84d5003e9b (PW-536)
blocked_by: []
relates: [PW-536, PW-471, PW-436, PW-435]
refs: [planet/timezoom/cycle.py, planet/timezoom/sim.py, "time zoom ae8f75", "time zoom 7ec3fe", "time zoom e9d59c", "run bf5ee9 @ 864 Myr"]
created: 2026-10-21
updated: 2026-10-23
---

## Description
On the run-based time zooms ae8f75 and 7ec3fe (seed 941637, L6, 864 Myr) the sea level shows no swing
with the glacial index (correlation 0.01). The sea-level bookkeeping is correct (see PW-536's Updates);
the zoom has almost no glacial forcing. `cooling()` is `glacial_cool x share / glacial_f` with `share`
the planet's ice-free land poleward of its snowline (`snowline_land`, which excludes land already under
ice). Here the share is 0.26% (Earth 3.49%), so the cooling is 0.49 C (Earth 6.49 C), dT_global at I = 0.94
is -0.26 C, and the sea-level target is -7 m. The run moment is also a warm world (dT +2.1 C) with 5.2% of
its surface already iced, so the ice that could grow is mostly there already.

Options (a physics/calibration call, parked with PW-470):
- A: count the land under grounded ice in the share (it is land a glacial iced over). Earth's share rises
  (Antarctica, Greenland) so `glacial_f` and `glacial_cool` need recalibrating on Earth.
- B: a floor on the cooling for any planet that cycles (a glacial is a glacial), e.g. a fraction of
  `glacial_cool`. A climate-agnostic floor is a stopgap.
- C: leave it: a planet with no free polar land has weak ice ages, and v1 accepts it.
Lean: A, with the start drift (PW-436) fixed first, since a diagnostic 5 C cooling on the same moment
(`--set glacial_dt=5`) only reaches corr(sea level, I) = -0.48 and sea level -28..+28 m, the glacial pick
+1 m against -8 m for the interglacial pick: the start drift and the weak sheet response (PW-435) still swamp it.
- [ ] After a fix, `finish.now_kyr(F.load_timezoom(<zoom of bf5ee9 @ 864 Myr>)[1], 'glacial')` picks a clearly lower sea level than 'interglacial'.
- [ ] Earth's zoom keeps cycles 98-109 kyr and maxima -86..-104 m.

## Updates
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-21: Owner 2026-10-21: moved to v2.
- 2026-10-21: Created from inbox draft draft-glacial-cooling-share-excludes-iced-land.md (found by worktree-agent-a1bb68a84d5003e9b (PW-536)).
