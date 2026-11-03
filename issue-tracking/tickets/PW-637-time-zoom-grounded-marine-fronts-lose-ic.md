---
id: PW-637
title: "Time zoom: grounded marine fronts lose ice only by the depth calving law; no ocean melt of the face, so a cold planet's marine sheets feel nothing of an ending's warming (the lever that clears PW-632's held branches)"
type: task
status: todo
parent: PW-470
milestone: later
subsystem: timezoom
effort: l
impact: med
found_by: base-climate-laneA19
blocked_by: []
relates: [PW-385, PW-632, PW-367, PW-588]
refs: [planet/timezoom/sim.py, planet/timezoom/fields.py, planet/ocean.py, docs/review/base-climate/laneA19/]
created: 2026-10-23
updated: 2026-11-03
---

## Description
The time zoom's grounded marine fronts (`_Sim.sea`) calve at `calving` x the water depth (m/yr) where they face open
water. Nothing else takes their ice: no ocean melt of the face, and no dependence on the sea's warmth.

**Why it matters:** on the cold worlds where PW-632's endings test fails, 55-70% of the glacial's leftover ice is
marine, 2.3-2.5 km thick on beds pushed below the sea. Lane A19's `hold.py` shows calving is the lever:
- With `calving` x4 the held share at I = 0 (120 kyr) falls from 17-51% to 0-8%, and 3 of the 4 failing cases pass.
- The index-off run's own ice hardly moves (mean sea level -66 -> -64 m, -27 -> -24 m).
So the marine margins decide whether a glacial's extra ice can leave. Raising the constant is tuning, though.

**The physics real terminations have** (Barents-Kara, Hudson Bay, Antarctica's shelf margins): warm subsurface water
at the front, which melts and undercuts the face.
- Tidewater frontal melt scales as ~ thermal forcing^1.2 x subglacial discharge^0.4 (Rignot et al. 2016; Slater et
  al. 2019).
- Undercutting raises calving 2-4x (O'Leary & Christoffersen 2013).

**What blocks it:** the model's ocean has only a surface temperature (PW-385). A probe
(`laneA19/front_melt_probe.diff`) adds 100-300 m/yr per C of the sea's annual water above freezing to the calving
speed. It moved only 1 of 4 cases: the cold worlds' fronts sit in water at freezing, at I = 0 as at a glacial.

**What to try:** after PW-385 gives the shelf seas a subsurface water temperature (the overturning's inflow, or a
deep-water profile with the global dT), add a frontal melt to the marine fronts' retreat, by that water's thermal
forcing and the front's summer meltwater discharge.
- [ ] Bar: PW-632's endings test on seeds 1-9 (L4 300 Myr, `laneA19/scan.py`) with extra > 10 m, both trees.
- [ ] Earth's `tz_earth.py --dt0` no worse.
- [ ] Earth's glacials still -80 m or deeper.

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Created from inbox draft draft-marine-fronts-no-ocean-melt.md (found by base-climate-laneA19).
