---
id: PW-455
title: The run's global temperature has no vegetation albedo term (the time zoom has one since PW-450)
type: task
status: todo
parent: PW-470
milestone: later
subsystem: climate
effort: s
impact: low
found_by: pw450
blocked_by: []
relates: [PW-450, PW-453]
refs: [planet/tectonics/earth.py, planet/timezoom/plants.py]
created: 2026-10-20
updated: 2026-11-03
---

## Description
In the run (`earth.update_climate`), the vegetation feeds back on the climate only locally, through
climate.compute's veg: Budyko w, and albedo_warming at albedo_k 0.03 C per W/m2, capped at 2 C, "the
air mixes it away". `earth.global_temperature` has no global term for it. Since PW-450, the time zoom
adds one: the change in the planet's albedo since the start x veg_toa 0.4 x veg_lambda 0.8 C per W/m2.
It counts from the start, so the two agree at a zoom's start. But a run's slow vegetation changes (land
plants appearing, the plant groups' timeline, a continent drifting under the boreal belt) have no global
albedo effect, while the time zoom's 10-kyr changes do.
Options: (A) leave it. The run's dT is a drift, CO2 and ice random walk, calibrated as a whole, and
vegetation changes there are slow and mixed into the drift. (B) Add the same term to
`global_temperature`, counted against a slow average like its CO2 terms. That would also need the cold
eras re-measured (PW-438's table). Lean: A, unless the plant groups' arrival shows a visible warm/cold
step that the run ought to have.

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created from inbox draft draft-run-no-global-vegetation-albedo.md (found by pw450).
