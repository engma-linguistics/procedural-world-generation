---
id: PW-240
title: "Run ice: after PW-190 still -300..-350 m in the coldest eras of seeds 2 and 11"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: icemb
blocked_by: []
relates: [PW-190, PW-235]
refs: [planet/icemass.py, planet/tectonics/earth.py]
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
- 2026-10-15: Status needs-decision -> todo. Coordinator decision (north star): follow the agent's lean: narrow the run's climate drift (~2 C sd) first, then lower the local snow damping once Earth's ice inception has its own fix (PW-033). For after the machine move.
- 2026-10-15: Created from inbox draft draft-run-ice-cold-eras-still-large.md (found by icemb).
