---
id: PW-435
title: "Earth time zoom's glacial is shallower after PW-366's margin fixes (150 kyr: -76 -> -33 m)"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: med
found_by: pw366
blocked_by: []
relates: [PW-033, PW-030, PW-366, PW-422]
refs: [planet/timezoom.py]
created: 2026-10-19
updated: 2026-10-20
---

## Description
PW-366 applies the time zoom's mass balance within the flow's sub-steps and gives bare land beside a sheet a
new edge's balance (bright, `edge_h` high). Before, the flow left a film of ice beyond each front for a step,
which hid the front from the margin rule (PW-422), so fronts took the interior's snow and advanced. Earth L6
default time zoom (`source_earth(6)`, default params), sea level change:
- old (4ce59df): 20 kyr -7, 50 kyr -16, 100 kyr -36, 150 kyr -76 m (ice 28 -> 60 Mkm3)
- new: 20 kyr -8, 50 kyr 0, 100 kyr -5, 150 kyr -18 m, deepest -33 m at 108 kyr (ice 28 -> 36 Mkm3)
- unforced 20 kyr: old -7, new -7 m.
Observed LGM ~-120 m. Part of the old glacial came from the film flaw; the remaining growth is now limited by
how fast a front advances onto bare land (one ring per ~step at best, under an edge's balance). PW-033's
inception (Fennoscandia, Laurentide) and the sub-cell margin of PW-115 / PW-422 are where to look.
- [ ] Earth's 150 kyr glacial back toward -60..-120 m by physics (inception, sub-cell margins), not by tuning
  the forcing

## Updates
- 2026-10-20: pw448: a near-linear ice albedo (draft, needs-decision) deepens Earth to -71 m in 600 kyr (-75 with co2_cool 4.0, area-mean -5.1 C), but the Laurentide stays ~2 Mkm2 with its southmost ice at ~55 N and the new ice goes to Siberia and Alaska. The rest of the depth and the geography are this ticket's and PW-033's (docs/review/audit/PW-448-diagnosis.md).
- 2026-10-20: pw440: with PW-440's cycle Earth is unchanged (min -43 m in 600 kyr, glacials ~30 m of extra ice against the 29 m an ending needs; one ending, one backstop); the 80 m swing needs this ticket's deeper builds.
- 2026-10-19: pw030: the run's ice-albedo rule in the time zoom deepens it to -37 m in 150 kyr (-43 m in 500 kyr). Unforced Earth with dT -3 C reaches -60 m, -5 C -137 m in 150 kyr: the glacial needs ~-4.5 C, the feedbacks give ~-1.5 C at -40 m.
- 2026-10-19: Created from inbox draft draft-earth-timezoom-glacial-shallower-pw366.md (found by pw366).
