---
id: PW-240
title: "Run ice: after PW-190 still -300..-350 m in the coldest eras of seeds 2 and 11"
type: task
status: done
parent: PW-244
subsystem: climate
effort: m
impact: med
found_by: icemb
blocked_by: []
relates: [PW-190, PW-235]
refs: [planet/icemass.py, planet/tectonics/earth.py, docs/review/health/2026-10-15/report.md, tools/health.py, docs/review/audit/pw293-sea-level.md, docs/review/health-pw293-after/report.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-190 option C shipped (icemb): one surface mass balance (`icemass.py`) for the run, the time zoom
and the zoom; the run's ice is the flowing sheets' extent under it averaged over the orbital cycle
(accumulation zone + a budget-paid ablation zone); dT counts the ice's albedo from Earth's present ice;
weathering faster when warm (0.12/C) and none under ice (PW-235). L6, 1 Gyr, sea level from ice,
mean / worst / share of time below -150 m, and dT min / share below -9 C:

| seed | before (main, 2026-10-15 am) | after, on merged main |
|---|---|---|
| 3199 | -45 / -119 / 0% ; -7.4 C | -63 / -218 / 6% ; -4.8 C |
| 11 | -65 / -412 / 14% ; -13.7 C, 7% | -76 / -354 / 18% ; -11.9 C, 2% |
| 2 | -69 / -273 / 15% ; -13.6 C, 10% | -104 / -350 / 33% ; -12.2 C, 3% |
| 21 | -22 / -98 / 0% ; -6.6 C | -30 / -139 / 0% ; -4.5 C |

(Before the merge of tectfound/hydro2, the same code gave 3199 -40/-241, 11 -37/-299, 2 -59/-232,
21 -38/-162: the merged tectonics changed the geography.) The time zoom's extra fall is now small
(typical moment -68..-144 m, coldest -56..-239 m; before 13-321 and 234-282 m), and Earth's 150 kyr
time zoom reaches -100 m. The physics is consistent: a planet whose *average* climate is LGM-cold
(dT -5 and below) holds LGM-scale ice on average; at the same dT Earth's time zoom has ~7-9% ice.
What remains is how long and how cold the cold eras are, and Earth's need for the lying snow's local
damping (draft on Earth glaciation), which also makes generated planets' snowfields last.
Options:
- A. Accept: cold eras are LGM-like or colder and hold that much ice.
- B. Weaker local damping (`icemass.LOCAL` 0.3 -> 0.15: ~-25 m at a dT -4 moment) and fix Earth's
  inception separately (draft on Earth glaciation).
- C. A stronger thermostat on the drift (the drift is an OU of sd 3 C; with ice albedo up to 3 C it
  makes the -10 C eras), e.g. smaller `climate_drift`.
Lean: C (smaller drift sd, ~2 C) plus B once Earth's inception has its own fix.

## Updates
- 2026-10-15: Merged inbox draft draft-icehouse-sea-below-envelope.md ("Seed 11's 180-232 Myr icehouse: total sea level now -370 m (ice -264, basins ~-100) since the +140 m basin offset went (PW-293)", found by pw293).
  health --quick after PW-293 (L6 seed 11, 500 Myr): the 180-232 Myr cold era (global 3.5-5 C) reaches a total
  sea level of -370 m at 188 Myr, ice -264 m and the ocean basins ~-105 m (an old ocean during assembly); 14
  keyframes below -200 m total or -150 m from ice, 2 sea_level spells below the health envelope's -250 m. It
  is the same era PW-308's 1 Gyr sweep showed at -322 m of ice, so the ice depth is not new; what is new is that
  the basins no longer add the old reference's +140 m, so the total shows it. The ice part is PW-308's /
  PW-240's question (Earth's LGM ~-120 m; PW-240's goal -150 typical / -250 worst). Decide whether a -260 m
  ice era at 3.5 C global is acceptable (the planet is ~11 C colder than today, colder than the LGM) or the run's
  ice is still too deep at that temperature. No change suggested to the basin term.
- 2026-10-15: Status todo -> done. Post-audit 1 Gyr sweep (docs/review/after-audit-2026-10-15/health): deepest ice sea level -9..-48 m on all 11 seeds (was -96..-384); no frames below -150 m. Too-deep cold eras are fixed; the opposite problem (runs barely glaciate) is a new ticket.
- 2026-10-15: After all audit fixes (climate merge 7f9cc82, measured by the climate agent on the merged code): health --quick deepest ice sea level s11 -71, s42 -15, s3199 -12 m; no frames below -150 m. Confirm in the post-batch 1 Gyr sweep.
- 2026-10-15: Ice fixes (PW-274..277, merged 20684ed): health --quick worst ice sea level s11 -360 -> -247, s42 -304 -> -124, s2 -174 -> -115 m; only s11 below -150 m (8.7% of frames). Climate fixes pending merge also move it.
- 2026-10-15: Merged inbox draft draft-health-pw240-cold-eras.md ("PW-240 update: health sweep cold eras: L6 seed 11 -384 m ice sea level (1 C) when its supercontinent drops to 4 plates; seeds 2, 77, 3199 to -205..-231 m", found by health-sweep).
  Update for PW-240. PW-246 health sweep (2026-10-15, main 6926583, default params, 1 Gyr, keyframes
  every 4 Myr; ice sea level = -0.9 x land ice volume / ocean area, as `earth.update_climate`):
  | seed, level | worst ice sea level | keyframes < -150 m / < -250 m (of 238) | coldest global T |
  |---|---|---|---|
  | 11 L6 | -384 m @ 188 Myr | 17 / 13 | 1.0 C @ 180 |
  | 77 L6 | -231 m @ 444 | 14 / 0 | 6.1 C @ 148 |
  | 2 L6 | -223 m @ 608 | 21 / 0 | 3.5 C @ 496 |
  | 3199 L6 | -205 m @ 480 | 17 / 0 | 9.5 C @ 504 |
  | 505 L6 | -154 m @ 596 | 3 / 0 | 10.9 C |
  | 1, 21, 42 L6 | -96..-131 m | 0 | 7.3-9.0 C |
  | 3199 / 21 / 11 L7 | -108 / -125 / -137 m | 0 | 9.4 / 9.2 / 5.4 C |
  So L7 stays inside the -150 m goal on all three seeds, and 4 of 8 L6 seeds dip below it for 3-9% of
  the run; only seed 11 at L6 passes -250 m. Its cold era (164-216 Myr) is a supercontinent (largest
  landmass 32-33% of the surface) whose plate count falls to 4-5 while the CO2 index drops to -1.1..-1.2
  (the arc/ridge source collapsing with the plates): T 8.7 C at 144 Myr -> 2.2 C at 176 -> 1.0 C at 184,
  ice 1.6% -> 13% of the surface, ice sea level -23 -> -384 m, recovering only slowly (-320 m at 216 Myr)
  as plates return. Total sea level (with the ocean-basin term) reaches -548 m there. The L7 run of
  seed 11 (9068cb, kept) has the same era colder than average but milder (5.4 C at 180 Myr, -137 m),
  with 8+ plates throughout. The L6 runs were deleted; they reproduce from seed + 6926583.
  - [ ] decide whether a few-plate supercontinent may glaciate this far (Earth's Cryogenian did, so a
    rare snowball-ish era may be acceptable) or whether the CO2 source should floor (volcanism not tied
    only to spreading and arcs)
- 2026-10-15: Status needs-decision -> todo. Coordinator decision (north star): follow the agent's lean: narrow the run's climate drift (~2 C sd) first, then lower the local snow damping once Earth's ice inception has its own fix (PW-033). For after the machine move.
- 2026-10-15: Created from inbox draft draft-run-ice-cold-eras-still-large.md (found by icemb).
